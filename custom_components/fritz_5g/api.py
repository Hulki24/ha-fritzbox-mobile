"""API for HA FRITZ!Box Mobile."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from fritzconnection import FritzConnection


class Fritz5GApi:
    """FRITZ!Box Mobile API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API."""

        self._host = host
        self._username = username
        self._password = password

    def get_info(self) -> dict:
        """Read GetInfoEx from the FRITZ!Box."""

        fc = FritzConnection(
            address=self._host,
            user=self._username,
            password=self._password,
        )

        return fc.call_action(
            "X_AVM-DE_WANMobileConnection1",
            "GetInfoEx",
        )

    def get_data(self) -> dict:
        """Return parsed mobile data."""

        info = self.get_info()

        data: dict = {
            "technology": info.get("NewCurrentAccessTechnology"),
        }

        signal = info.get("NewSignalRSRP0", "")

        match = re.search(
            r"main=(-?\d+)",
            signal,
        )

        if match:
            data["lte_rsrp"] = int(match.group(1))

        xml = info.get("NewCellList", "")

        if not xml:
            return data

        root = ET.fromstring(xml)

        for cell in root.findall("Cell"):

            cell_type = cell.findtext("CellType")

            if (
                cell_type == "lte"
                and cell.findtext("Connected") == "primary"
            ):

                rsrp = cell.findtext("RSRP")
                rsrq = cell.findtext("Rsrq")
                rssi = cell.findtext("Rssi")
                pci = cell.findtext("PhysicalId")
                distance = cell.findtext("Distance")

                data["provider"] = cell.findtext("Provider")
                data["lte_cell_id"] = cell.findtext("Cellid")
                data["serial_number"] = info.get("NewSerialNumber")
                data["firmware"] = info.get("NewSoftwareVersion")

                if rsrp:
                    data["lte_rsrp"] = int(rsrp)

                if rsrq:
                    data["lte_rsrq"] = int(rsrq)

                if rssi:
                    data["lte_rssi"] = int(rssi)

                if pci:
                    data["pci"] = int(pci)

                if distance:
                    data["distance"] = int(distance)

            elif cell_type == "nr5g":

                rsrp = cell.findtext("RSRP")
                rsrq = cell.findtext("Rsrq")
                rssi = cell.findtext("Rssi")

                data["nr_cell_id"] = cell.findtext("Cellid")

                if rsrp:
                    data["nr_rsrp"] = int(rsrp)

                if rsrq:
                    data["nr_rsrq"] = int(rsrq)

                if rssi:
                    data["nr_rssi"] = int(rssi)

        return data
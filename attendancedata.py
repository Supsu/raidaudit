from dataclasses import dataclass


@dataclass
class AttendanceData:
    """
    Contains data about the attendance of a player
    """
    player_name: str = ""
    raid_id: int = 0
    raid_name: str = ""
    present_total: int = 0
    present_active: int = 0
    present_benched: int = 0

    def __str__(self):
        return f"{self.player_name}: {self.present_total} ({self.present_active}/{self.present_benched})"
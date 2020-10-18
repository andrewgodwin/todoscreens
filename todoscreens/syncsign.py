from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple
import requests


ColorType = Literal["WHITE", "BLACK"]


class SyncSignClient:
    """
    A simple client for SyncSign
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sync-sign.com/v2/key/%s" % self.api_key

    def node_list(self) -> List["Node"]:
        response = requests.get("%s/nodes" % self.base_url)
        assert response.status_code == 200
        result = []
        for item in response.json()["data"]:
            result.append(Node(id=item["nodeId"], model=item["model"]))
        return result

    def node_draw(self, node_id, layout: "Layout"):
        """
        Draws content to the screen of a node.
        """
        response = requests.post(
            "%s/nodes/%s/renders" % (self.base_url, node_id.lower()),
            json={"layout": layout.export()},
        )
        assert response.status_code == 200
        data = response.json()
        assert list(data["data"].values()) == [{"posted": True}], (
            "Bad response: %s" % data
        )


@dataclass
class Node:
    id: str
    model: str


class Layout:
    """
    Represents a top-level render
    """

    def __init__(
        self,
        items=None,
        background: ColorType = "WHITE",
        button_zone: bool = False,
        poll_rate: int = 10000,
    ):
        self.items = items or []
        self.background = background
        self.button_zone = button_zone
        self.poll_rate = poll_rate

    def export(self):
        return {
            "background": {
                "bgColor": self.background,
                "enableButtonZone": self.button_zone,
            },
            "items": [item.export() for item in self.items],
            "options": {"pollRate": self.poll_rate, "refreshScreen": True},
        }

    def add(self, item):
        self.items.append(item)


class Text:
    """
    A text item on a display
    """

    def __init__(
        self,
        text: str,
        position: Tuple[int, int],
        size: Tuple[int, int] = (400, 300),
        offset: Tuple[int, int] = (0, 0),
        font: str = "DDIN_32",
        color: ColorType = "BLACK",
        background_color: ColorType = "WHITE",
        align: Literal["LEFT", "RIGHT", "CENTER"] = "LEFT",
    ):
        self.text = text
        self.position = position
        self.size = size
        self.offset = offset
        self.font = font
        self.color = color
        self.background_color = background_color
        self.align = align

    def export(self):
        return {
            "type": "TEXT",
            "data": {
                "text": self.text,
                "id": str(id(self)),
                "textColor": self.color,
                "backgroundColor": self.background_color,
                "font": self.font,
                "textAlign": self.align,
                "lineSpace": 0,
                "block": {
                    "x": self.position[0],
                    "y": self.position[1],
                    "w": self.size[0],
                    "h": self.size[1],
                },
                "offset": {"x": self.offset[0], "y": self.offset[1]},
            },
        }


class BottomButtons:
    """
    Represents bottom buttons
    """

    def __init__(self, buttons: List[Tuple[str, bool]]):
        self.buttons = buttons

    def export(self):
        buttons_list = []
        for title, enabled in self.buttons[:4]:
            buttons_list.append(
                {"title": title, "style": "ENABLED" if enabled else "DISABLED"}
            )
        while len(buttons_list) < 4:
            buttons_list.append({"title": "-", "style": "BLANK"})
        return {
            "type": "BOTTOM_CUSTOM_BUTTONS",
            "data": {"list": buttons_list},
        }


class Rectangle:
    """
    A rectangle
    """

    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        fill: Optional[ColorType] = None,
        stroke: Optional[ColorType] = None,
        stroke_width: int = 1,
    ):
        self.position = position
        self.size = size
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width

    def export(self):
        value = {
            "type": "RECTANGLE",
            "data": {
                "strokeThickness": self.stroke_width,
                "block": {
                    "x": self.position[0],
                    "y": self.position[1],
                    "w": self.size[0],
                    "h": self.size[1],
                },
            },
        }
        if self.fill:
            value["data"]["fillColor"] = self.fill
        if self.stroke:
            value["data"]["strokeColor"] = self.stroke

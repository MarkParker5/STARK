from fastapi import FastAPI
from sqladmin import Admin, ModelAdmin, SidebarLink
from Controls.API.dependencies import database
from Controls.API.models import (
    Base,
    House,
    Hub,
    Room,
    DeviceModel,
    Device,
    Parameter,
)


class HouseAdmin(ModelAdmin, model = House):
    icon = 'fa-solid fa-house'
    column_list = [House.name]
    column_details_exclude_list = [House.id]
    form_excluded_columns = [House.id]

class HubAdmin(ModelAdmin, model = Hub):
    icon = 'fa-solid fa-wifi'
    column_list = [Hub.name, Hub.house]
    column_details_exclude_list = [Hub.id, Hub.house_id]
    form_excluded_columns = [Hub.id, Hub.house_id]

class RoomAdmin(ModelAdmin, model = Room):
    icon = 'fa-solid fa-house-user'
    column_list = [Room.name, Room.house]
    column_details_list = [Room.name, Room.house, Room.devices]

class DeviceModelAdmin(ModelAdmin, model = DeviceModel):
    icon = 'fa-solid fa-lightbulb'
    column_list = [DeviceModel.name, DeviceModel.parameters]
    column_details_list = [DeviceModel.name, DeviceModel.parameters]

class DeviceAdmin(ModelAdmin, model = Device):
    icon = 'fa-solid fa-microchip'
    column_list = [Device.name, Device.urdi, Device.model, Device.room]
    column_details_list = [Device.name, Device.urdi, Device.model, Device.room]

class ParameterAdmin(ModelAdmin, model = Parameter):
    icon = 'fa-solid fa-sliders'
    column_list = [Parameter.name, Parameter.value_type]
    column_details_exclude_list = [Parameter.id]

links = [
    SidebarLink('API', '/docs', True),
]

def setup(app: FastAPI):
    admin = Admin(app,
        engine = database.engine,
        title = 'Archie Cloud - Admin',
        links = links
    )
    admin.register_model(HouseAdmin)
    admin.register_model(RoomAdmin)
    admin.register_model(HubAdmin)
    admin.register_model(DeviceModelAdmin)
    admin.register_model(DeviceAdmin)
    admin.register_model(ParameterAdmin)

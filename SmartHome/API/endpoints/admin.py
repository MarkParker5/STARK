from fastapi import FastAPI
from sqladmin import Admin, ModelAdmin, SidebarLink
from SmartHome.API.dependencies import database
from SmartHome.API.models import (
    Base,
    House,
    Hub,
    Room,
    DeviceModel,
    Device,
    Parameter,
    DeviceParameterAssociation
)


class HouseAdmin(ModelAdmin, model = House):
    icon = 'fa-solid fa-house'
    column_list = [House.name, House.rooms]
    column_details_exclude_list = [House.id]
    form_excluded_columns = [House.id]

class HubAdmin(ModelAdmin, model = Hub):
    icon = 'fa-solid fa-wifi'
    column_list = [Hub.name, Hub.house]
    column_details_exclude_list = [Hub.id, Hub.house_id]
    form_excluded_columns = [Hub.id, Hub.house_id]

class RoomAdmin(ModelAdmin, model = Room):
    icon = 'fa-solid fa-house-user'
    column_list = [Room.name, Room.house, Room.devices]
    column_details_list = [Room.name, Room.house, Room.devices]
    form_excluded_columns = [Room.house_id]

class DeviceModelAdmin(ModelAdmin, model = DeviceModel):
    icon = 'fa-solid fa-lightbulb'
    column_list = [DeviceModel.name, DeviceModel.parameters]
    column_details_list = [DeviceModel.name, DeviceModel.parameters]

class DeviceAdmin(ModelAdmin, model = Device):
    icon = 'fa-solid fa-microchip'
    column_list = [Device.name, Device.urdi, Device.model, Device.room, Device.parameters]
    column_details_list = [Device.name, Device.urdi, Device.model, Device.room, Device.parameters]
    form_excluded_columns = [Device.room_id, Device.model_id, Device.parameters]

class ParameterAdmin(ModelAdmin, model = Parameter):
    icon = 'fa-solid fa-sliders'
    column_list = [Parameter.name, Parameter.value_type]
    column_details_exclude_list = [Parameter.id, Parameter.device_parameters]
    form_excluded_columns = [Parameter.device_parameters]

class DeviceParameterAdmin(ModelAdmin, model = DeviceParameterAssociation):
    name = 'Device Parameter'
    name_plural = 'Device Parameters'
    icon = 'fa-solid fa-gears'
    column_list = [DeviceParameterAssociation.device, DeviceParameterAssociation.parameter, DeviceParameterAssociation.value]
    column_details_list = column_list
    form_columns = column_list

links = [
    SidebarLink('API', '/docs', True),
]

def setup(app: FastAPI):
    admin = Admin(app,
        engine = database.engine,
        title = 'Archie Hub - Admin',
        links = links
    )
    admin.register_model(HouseAdmin)
    admin.register_model(RoomAdmin)
    admin.register_model(HubAdmin)
    admin.register_model(DeviceModelAdmin)
    admin.register_model(DeviceAdmin)
    admin.register_model(ParameterAdmin)
    admin.register_model(DeviceParameterAdmin)

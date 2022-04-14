houses = DBTable('houses', {
    'name': 'text',
    'owner_id': 'text'
})

rooms = DBTable('rooms', {
    'name': 'text',
})

devices = DBTable('devices', {
    'name': 'text',
    'urdi': 'blob',
    'room_id': 'text',
    'model_id': 'text'
})

deviceModels = DBTable('device_models', {
    'name': 'text',
})

parameters = DBTable('parameters', {
    'name': 'text',
})

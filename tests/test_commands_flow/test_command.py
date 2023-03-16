from VICore import CommandsManager, Response


def test_call_command_from_command():
    manager = CommandsManager()
    
    @manager.new('foo')
    def foo() -> Response: 
        return Response(text = 'foo!')
    
    @manager.new('bar')
    def bar() -> Response: 
        return foo()
    
    assert bar().text == 'foo!'
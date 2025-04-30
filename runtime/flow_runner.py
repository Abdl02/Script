class FlowRunner{
    def __init__(self, flow):
        self.flow = flow
        self.state = None
        self.result = None
        self.exception = None
        self.start_time = None
        self.end_time = None
        self.status = None
        self._initialize_flow()
        self._initialize_state()
        self._initialize_result()
        self._initialize_exception()
        self._initialize_start_time()
        self._initialize_end_time()
        self._initialize_status()
}
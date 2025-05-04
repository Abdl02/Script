from config.envModel import envs


class Config:
    # Static variable to store the selected environment
    selected_env_name = None
    selected_env = None

    @staticmethod
    def set_selected_env(envName: str):
        """
        Set the selected environment.
        :param env: The name of the environment to set.
        """
        Config.selected_env_name = envName
        Config.selected_env = envs.get(envName)
        if not Config.selected_env:
            raise ValueError(f"Environment '{envName}' not found.")
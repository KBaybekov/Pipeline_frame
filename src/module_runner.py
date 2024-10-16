from src.utils import generate_sample_list, generate_cmd_data, save_yaml, get_paths, create_paths
from src.pipeline_manager import PipelineManager
from src.command_executor import CommandExecutor
import os

class ModuleRunner:
    def __init__(self, pipeline_manager: PipelineManager):
        #Данные, получаемые из pipeline_manager.modules_template
        self.folders: dict
        self.source_extensions: tuple
        self.filenames: dict
        self.commands: dict
        self.subfolder:str
        
        # Собственные данные класса
        self.cmd_data: dict

        self.pipeline_manager = pipeline_manager


    def run_module(self, module:str, module_result_dict:dict) -> dict:
        # Цвета!
        BLUE = "\033[34m"
        WHITE ="\033[37m"

        # Алиас
        x = self.pipeline_manager

        # Загружаем данные о модуле в пространство класса
        self.load_module(x.modules_template[module], x.input_dir, x.output_dir)

        # Получаем список образцов
        self.samples = generate_sample_list(in_samples=x.include_samples, ex_samples=x.exclude_samples,
                                            input_dir=f'{x.input_dir}/{self.subfolder}/',
                                            extensions=self.source_extensions, subfolders=x.subfolders)
        # Генеририруем команды
        self.cmd_data = generate_cmd_data(args=x.__dict__, folders=self.folders,
                                    executables=x.executables, filenames=self.filenames,
                                    cmds_dict=self.commands, commands=x.cmds_template, samples=self.samples,
                                    subfolder=self.subfolder)
        # Логгируем сгенерированные команды для модуля
        save_yaml(f'cmd_data_{module}', x.log_dir, self.cmd_data)
        # Если режим демонстрации активен, завершаем выполнение
        if x.demo == 'yes':
            exit()

        # Алиас
        c = self.cmd_data

        # Создаём пути
        create_paths(list(self.folders.values()))
        # Инициализируем CommandExecutor
        exe = CommandExecutor(cmd_data=c, log_space=x.log_space, module=module)

        # Выполняем команды для каждого образца
        print(f'Module: {BLUE}{module}{WHITE}')
        module_result_dict = exe.execute(c.keys(), module_result_dict)
        
        '''# Если модуль завершился с ошибкой - передаём это наверх
        if not module_result_dict['status']:
            module_result_dict['status'] = False'''

        return module_result_dict
        

    def load_module(self, data:dict, input_dir:str, output_dir:str):
        """
        Загружает данные о модуле, обрабатывает их с использованием переменных в пространстве класса и\
                добавляет их в пространство объекта класса.
        """
        # Составляем полные пути для папок
        data['folders'] = get_paths(data['folders'], input_dir, output_dir)
        # Устанавливаем атрибут modules_data в пространство экземпляра класса
        for key,value in data.items():
            if key == 'source_extensions':
                #Модифицируем список в кортеж для дальнейшего использования
                setattr(self, key, tuple(value))
                continue
            # Если ключ 'commands' и значение пустое, назначаем пустой список
            if key == 'commands':
                for group, val in data[key].items():
                    if val is None:
                        data[key][group] = []
            if key == 'subfolder':
                if value is None:
                    data[key] = ''
            setattr(self, key, value)
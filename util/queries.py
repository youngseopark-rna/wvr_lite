select_model_name = "SELECT [Model Name] FROM [T_Models]"

select_table_name = "SELECT [Table Name] FROM [T_Table_Mapping]"


def select_all_datas(table_name: str):
    return f"SELECT * FROM [{table_name}]"

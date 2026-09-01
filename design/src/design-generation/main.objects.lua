--version  = 1
--Eplanner version = 2026.1.9523.22553
--PAC_name = 'O1-Моцарелла'
------------------------------------------------------------------------------
------------------------------------------------------------------------------
init_tech_objects_modes = function()
    return
    {
    [ 1 ] =
        {
        n          = 1,
        tech_type  = 1,
        name       = 'Ячейка процесса',
        name_eplan = 'MASTER',
        name_BC    = 'MasterObj',
        cooper_param_number = -1,
        base_tech_object = 'master',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время операции',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время шага',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Номер первого танка в очереди O7 ALPMA',
                value = 0,
                meter = '№',
                oper = { 6 },
                nameLua = 'ENQ_O7_TANK1_ALPMA'
                },
            [ 4 ] =
                {
                name = 'Номер второго танка в очереди O7 ALPMA (Резерв)',
                value = 0,
                meter = '№',
                oper = { 6 },
                nameLua = 'ENQ_O7_TANK2_ALPMA'
                },
            [ 5 ] =
                {
                name = 'Номер третьего танка в очереди O7 ALPMA (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK3_ALPMA'
                },
            [ 6 ] =
                {
                name = 'Номер четвертого танка в очереди O7 ALPMA (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK4_ALPMA'
                },
            [ 7 ] =
                {
                name = 'Номер пятого танка в очереди O7 ALPMA (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK5_ALPMA'
                },
            [ 8 ] =
                {
                name = 'Номер первого танка в очереди F_BRINE_IN',
                value = 0,
                meter = '№',
                oper = { 7 },
                nameLua = 'ENQ_F_BRINE_IN_TANK1'
                },
            [ 9 ] =
                {
                name = 'Номер второго танка в очереди F_BRINE_IN',
                value = 0,
                meter = '№',
                oper = { 7 },
                nameLua = 'ENQ_F_BRINE_IN_TANK2'
                },
            [ 10 ] =
                {
                name = 'Номер третьего танка в очереди F_BRINE_IN (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_F_BRINE_IN_TANK3'
                },
            [ 11 ] =
                {
                name = 'Номер четвертого танка в очереди F_BRINE_IN (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_F_BRINE_IN_TANK4'
                },
            [ 12 ] =
                {
                name = 'Номер первого танка в очереди F_BRINE_OUT',
                value = 0,
                meter = '№',
                oper = { 8 },
                nameLua = 'ENQ_F_BRINE_OUT_TANK1'
                },
            [ 13 ] =
                {
                name = 'Номер второго танка в очереди F_BRINE_OUT',
                value = 0,
                meter = '№',
                oper = { 8 },
                nameLua = 'ENQ_F_BRINE_OUT_TANK2'
                },
            [ 14 ] =
                {
                name = 'Номер третьего танка в очереди F_BRINE_OUT (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_F_BRINE_OUT_TANK3'
                },
            [ 15 ] =
                {
                name = 'Номер четвертого танка в очереди F_BRINE_OUT (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_F_BRINE_OUT_TANK4'
                },
            [ 16 ] =
                {
                name = 'Номер первого танка в очереди W2',
                value = 0,
                meter = '№',
                oper = { 13 },
                nameLua = 'ENQ_W2_TANK1'
                },
            [ 17 ] =
                {
                name = 'Номер второго танка в очереди W2 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_W2_TANK2'
                },
            [ 18 ] =
                {
                name = 'Номер третьего танка в очереди W2 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_W2_TANK3'
                },
            [ 19 ] =
                {
                name = 'Номер четвертого танка в очереди W2 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_W2_TANK4'
                },
            [ 20 ] =
                {
                name = 'Номер пятого танка в очереди W2 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_W2_TANK5'
                },
            [ 21 ] =
                {
                name = 'Номер первого танка дозирования рассола в очереди наполнения BRN4',
                value = 0,
                meter = '№',
                oper = { 14 },
                nameLua = 'ENQ_BRN4_TANK1'
                },
            [ 22 ] =
                {
                name = 'Номер второго танка дозирования рассола в очереди наполнения BRN4',
                value = 0,
                meter = '№',
                oper = { 14 },
                nameLua = 'ENQ_BRN4_TANK2'
                },
            [ 23 ] =
                {
                name = 'Номер третьего танка дозирования рассола в очереди наполнения BRN4 (Резерв)',
                value = 0,
                meter = '№',
                oper = { 14 },
                nameLua = 'ENQ_BRN4_TANK3'
                },
            [ 24 ] =
                {
                name = 'Номер четвертого танка дозирования рассола в очереди наполнения BRN4 (Резерв)',
                value = 0,
                meter = '№',
                oper = { 14 },
                nameLua = 'ENQ_BRN4_TANK4'
                },
            [ 25 ] =
                {
                name = 'Номер первого танка в очереди O7 BERTSCH',
                value = 0,
                meter = '№',
                oper = { 15 },
                nameLua = 'ENQ_O7_TANK1_BERTSCH'
                },
            [ 26 ] =
                {
                name = 'Номер второго танка в очереди O7 BERTSCH (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK2_BERTSCH'
                },
            [ 27 ] =
                {
                name = 'Номер третьего танка в очереди O7 BERTSCH (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK3_BERTSCH'
                },
            [ 28 ] =
                {
                name = 'Номер четвертого танка в очереди O7 BERTSCH (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK4_BERTSCH'
                },
            [ 29 ] =
                {
                name = 'Номер пятого танка в очереди O7 BERTSCH (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O7_TANK5_BERTSCH'
                },
            [ 30 ] =
                {
                name = 'Номер первого танка в очереди O8',
                value = 0,
                meter = '№',
                oper = { 16 },
                nameLua = 'ENQ_O8_TANK1'
                },
            [ 31 ] =
                {
                name = 'Номер второго танка в очереди O8 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O8_TANK2'
                },
            [ 32 ] =
                {
                name = 'Номер третьего танка в очереди O8 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O8_TANK3'
                },
            [ 33 ] =
                {
                name = 'Номер четвертого танка в очереди O8 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O8_TANK4'
                },
            [ 34 ] =
                {
                name = 'Номер пятого танка в очереди O8 (Резерв)',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'ENQ_O8_TANK5'
                },
            [ 35 ] =
                {
                name = 'Номер 1 в очереди линии наполнения воды WLINE10',
                value = 0,
                meter = '№',
                oper = { 21 },
                nameLua = 'ENQ_NUMBER1_WLINE10'
                },
            [ 36 ] =
                {
                name = 'Номер 2 в очереди линии наполнения воды WLINE10',
                value = 0,
                meter = '№',
                oper = { 21 },
                nameLua = 'ENQ_NUMBER2_WLINE10'
                },
            [ 37 ] =
                {
                name = 'Номер 3 в очереди линии наполнения воды WLINE10',
                value = 0,
                meter = '№',
                oper = { 21 },
                nameLua = 'ENQ_NUMBER3_WLINE10'
                },
            [ 38 ] =
                {
                name = 'Номер 1 в очереди линии выдачи воды WR1',
                value = 0,
                meter = '№',
                oper = { 22 },
                nameLua = 'ENQ_NUMBER1_WR1'
                },
            [ 39 ] =
                {
                name = 'Номер 2 в очереди линии выдачи воды WR1',
                value = 0,
                meter = '№',
                oper = { 22 },
                nameLua = 'ENQ_NUMBER2_WR1'
                },
            [ 40 ] =
                {
                name = 'Номер 3 в очереди линии выдачи воды WR1',
                value = 0,
                meter = '№',
                oper = { 22 },
                nameLua = 'ENQ_NUMBER3_WR1'
                },
            [ 41 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 42 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 43 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 44 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 45 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 46 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 47 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 48 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 49 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 50 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        system_parameters =
            {
            P_MIX_FLIP_PERIOD =
                {
                value = 60,
                },
            P_MIX_FLIP_UPPER_TIME =
                {
                value = 2000,
                },
            P_MIX_FLIP_LOWER_TIME =
                {
                value = 1500,
                },
            P_V_OFF_DELAY_TIME =
                {
                value = 2500,
                },
            P_V_BOTTOM_OFF_DELAY_TIME =
                {
                value = 2000,
                },
            P_WAGO_TCP_NODE_WARN_ANSWER_AVG_TIME =
                {
                value = 50,
                },
            P_MAIN_CYCLE_WARN_ANSWER_AVG_TIME =
                {
                value = 300,
                },
            P_RESTRICTIONS_MODE =
                {
                value = 0,
                },
            P_RESTRICTIONS_MANUAL_TIME =
                {
                value = 120000,
                },
            P_AUTO_PAUSE_OPER_ON_DEV_ERR =
                {
                value = 0,
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Приготовление партии продукта в танке №1',
                },
            [ 2 ] =
                {
                name = 'Приготовление партии продукта в танке №2 (Резерв)',
                },
            [ 3 ] =
                {
                name = 'Приготовление партии продукта в танке №3 (Резерв)',
                },
            [ 4 ] =
                {
                name = 'Приготовление партии продукта в танке №4 (Резерв)',
                },
            [ 5 ] =
                {
                name = 'Приготовление партии продукта в танке №5 (Резерв)',
                },
            [ 6 ] =
                {
                name = 'Наполнение танков по линии O7 ALPMA',
                },
            [ 7 ] =
                {
                name = 'Линия наполнения водой (Танки дозирования рассола) F_BRINE_IN',
                },
            [ 8 ] =
                {
                name = 'Линия выдачи (Танки дозирования рассола) F_BRINE_OUT',
                },
            [ 9 ] =
                {
                name = 'Приготовление партии продукта в танке доз. рассола №1',
                },
            [ 10 ] =
                {
                name = 'Приготовление партии продукта в танке доз. рассола №2',
                },
            [ 11 ] =
                {
                name = 'Приготовление партии продукта в танке доз. рассола №3 (Резерв)',
                },
            [ 12 ] =
                {
                name = 'Приготовление партии продукта в танке доз. рассола №4 (Резерв)',
                },
            [ 13 ] =
                {
                name = 'Выдача из танков по линии W2',
                },
            [ 14 ] =
                {
                name = 'Наполнение танков дозирования рассола по линии BRN4',
                },
            [ 15 ] =
                {
                name = 'Наполнение танков по линии O7 BERTSCH',
                },
            [ 16 ] =
                {
                name = 'Наполнение танков по линии O8',
                },
            [ 17 ] =
                {
                name = 'Приготовление партии продукта в танке воды №1',
                },
            [ 18 ] =
                {
                name = 'Приготовление партии продукта в танке воды №2 (Резерв)',
                },
            [ 19 ] =
                {
                name = 'Приготовление партии продукта в танке воды №3 (Резерв)',
                },
            [ 20 ] =
                {
                name = 'Приготовление партии продукта в танке воды №4 (Резерв)',
                },
            [ 21 ] =
                {
                name = 'Наполнение танков воды по линии WLINE10',
                },
            [ 22 ] =
                {
                name = 'Выдача из танков воды по линии воды WR1',
                },
            [ 23 ] =
                {
                name = 'Новая операция',
                },
            [ 24 ] =
                {
                name = 'Новая операция',
                },
            [ 25 ] =
                {
                name = 'Новая операция',
                },
            [ 26 ] =
                {
                name = 'Новая операция',
                },
            [ 27 ] =
                {
                name = 'Новая операция',
                },
            [ 28 ] =
                {
                name = 'Новая операция',
                },
            [ 29 ] =
                {
                name = 'Новая операция',
                },
            [ 30 ] =
                {
                name = 'Выдача воды WLINE5->BERTSCH ',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'BERTSCH_MOZ_GW1DI52', 'WLINE5DO12' }, 0, },
                            { { 'BERTSCH_MOZ_GW1DI52', 'BERTSCH_MOZ_GW1DO53' }, 0, },
                            { { 'WLINE5DI12', 'BERTSCH_MOZ_GW1DO52' }, 0, },
                            },
                        },
                    },
                },
            },
        },
    [ 2 ] =
        {
        n          = 4790,
        tech_type  = 2,
        name       = 'Подогреватель технол. воды HWP',
        name_eplan = 'P',
        name_BC    = 'P4790Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 10,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE4DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE4DI479004',
                    CIP_WASH_END = 'MCA5LINE4DI479005',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI479001',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4820V1', 'P4820V2', 'P4790V41', 'P4790V1', 'P4790V21'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE4DI1', 'ALPMAGW5DI479001'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE4DI479001', 'ALPMAGW5DO479001' }, 0, },
                            { { 'MCA5LINE4DI479002', 'ALPMAGW5DO479002' }, 0, },
                            { { 'MCA5LINE4DI479003', 'ALPMAGW5DO479003' }, 0, },
                            { { 'ALPMAGW5DI479001', 'MCA5LINE4DO479001' }, 0, },
                            { { 'ALPMAGW5DI479002', 'MCA5LINE4DO479002' }, 0, },
                            { { 'ALPMAGW5DI479003', 'MCA5LINE4DO479003' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4790V12', 'P4790V16'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'P4820V1'
                                        },
                                    },
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'P4820V2', 'P4790V1'
                                        },
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI479002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4790V13'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4790V12', 'P4790V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4790V13'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE4DI479004', 'ALPMAGW5DO479004' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4790V12', 'P4790V16', 'P4790V13'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                closed_devices = --Выключать
                                    {
                                    'ALPMAGW5DO479001'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO479005'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4790V12'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI482010',
                    WORK_FILL_AND_OUT = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'P4875V43', 'P4850V43', 'P4870V43', 'P4840V43', 'BUNKER1V43'
                            },
                        closed_devices = --Выключать
                            {
                            'P4790V43'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI479011'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4790V41'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Откачка жирводы',
                                time_param_n = -1,
                                next_step_n = -1,
                                enable_step_by_signal = --Сигнал для включения текущего шага
                                    {
                                    { 'ALPMAGW5DI479013' },
                                    true,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 3 ] =
        {
        n          = 4805,
        tech_type  = 3,
        name       = 'Буферный дренажный канал BDC-3000/A',
        name_eplan = 'P',
        name_BC    = 'P4805Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE3DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE3DI480504',
                    CIP_WASH_END = 'MCA5LINE3DI480505',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI480501',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE3DI1', 'ALPMAGW5DI480501'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE3DI480501', 'ALPMAGW5DO480501' }, 0, },
                            { { 'MCA5LINE3DI480502', 'ALPMAGW5DO480502' }, 0, },
                            { { 'MCA5LINE3DI480503', 'ALPMAGW5DO480503' }, 0, },
                            { { 'ALPMAGW5DI480501', 'MCA5LINE3DO480501' }, 0, },
                            { { 'ALPMAGW5DI480502', 'MCA5LINE3DO480502' }, 0, },
                            { { 'ALPMAGW5DI480503', 'MCA5LINE3DO480503' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4805V11', 'P4805V16', 'P4805V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI480502'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4805V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды ',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4805V11', 'P4805V16', 'P4805V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4805V12'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE3DI480504', 'ALPMAGW5DO480504' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4805V11', 'P4805V12', 'P4805V16', 'P4805V17'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4805V12', 'P4805V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4805V11', 'P4805V17', 'MCA5LINE3DO480501'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO480505'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4805V17'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI480510',
                    WORK_FILL_AND_OUT = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4805V11', 'P4805V12'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'ALPMAGW5DI480510'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'ALPMAGW5DI480511', 'ALPMAGW5DO480511' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4805V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4805V17'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 4 ] =
        {
        n          = 4820,
        tech_type  = 4,
        name       = 'Машина варки и вытяжки WCSLE-2000/A',
        name_eplan = 'P',
        name_BC    = 'P4820Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '14',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 150,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE1DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE1DI482004',
                    CIP_WASH_END = 'MCA5LINE1DI482005',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI482001',
                    NEED_HEATER_NODE = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4820V1', 'P4820V36', 'P4820V37', 'P4820V2'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE1DI1', 'ALPMAGW5DI482001'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE1DI482001', 'ALPMAGW5DO482001' }, 0, },
                            { { 'MCA5LINE1DI482002', 'ALPMAGW5DO482002' }, 0, },
                            { { 'MCA5LINE1DI482003', 'ALPMAGW5DO482003' }, 0, },
                            { { 'ALPMAGW5DI482001', 'MCA5LINE1DO482001' }, 0, },
                            { { 'ALPMAGW5DI482002', 'MCA5LINE1DO482002' }, 0, },
                            { { 'ALPMAGW5DI482003', 'MCA5LINE1DO482003' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = 17,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'P4820V11', 'P4820V16', 'P4820V17', 'P4820V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4820V13'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'P4820V2'
                                        },
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI482002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4820V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = 19,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4820V11', 'P4820V13', 'P4820V16', 'P4820V17', 'P4820V19'
                                    },
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'P4820V1'
                                        },
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI482002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4820V12'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4820V11', 'P4820V16', 'P4820V17', 'P4820V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4820V12'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE1DI482004', 'ALPMAGW5DO482004' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4820V11', 'P4820V12', 'P4820V16', 'P4820V17', 'P4820V19'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4820V12', 'P4820V16', 'P4820V13'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4820V11', 'P4820V17', 'P4820V19', 'MCA5LINE1DO482001'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO482005'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4820V17'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI482010',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_HEATER_NODE = 'true',
                    NEED_PAUSE_HEATER_NODE = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4820V11', 'P4820V12', 'P4820V13', 'P4790V16', 'P4790V13'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11', 'ALPMAGW5DI482010'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'ALPMAGW5DI482013', 'ALPMAGW5DO482013' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4820V16', 'P4820V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI482011'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4820V1'
                                            },
                                        },
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI482012'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4820V2'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 5 ] =
        {
        n          = 4835,
        tech_type  = 5,
        name       = 'Машина сухой посолки DS-1',
        name_eplan = 'P',
        name_BC    = 'P4835Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '15',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE4DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE4DI483504',
                    CIP_WASH_END = 'MCA5LINE4DI483505',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI483501',
                    NEED_HEATER_NODE = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4835V36'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE4DI1', 'ALPMAGW5DI483501'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE4DI483501', 'ALPMAGW5DO483501' }, 0, },
                            { { 'MCA5LINE4DI483502', 'ALPMAGW5DO483502' }, 0, },
                            { { 'MCA5LINE4DI483503', 'ALPMAGW5DO483503' }, 0, },
                            { { 'ALPMAGW5DI483501', 'MCA5LINE4DO483501' }, 0, },
                            { { 'ALPMAGW5DI483502', 'MCA5LINE4DO483502' }, 0, },
                            { { 'ALPMAGW5DI483503', 'MCA5LINE4DO483503' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4835V11', 'P4835V16', 'P4835V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4850V13'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI483502'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4835V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4835V11', 'P4835V16', 'P4835V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4835V12', 'P4850V13'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE4DI483504', 'ALPMAGW5DO483504' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4835V11', 'P4835V12', 'P4835V16', 'P4835V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4850V13'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4835V12', 'P4835V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4835V11', 'P4835V17', 'P4850V13', 'MCA5LINE4DO483501'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO483505'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4835V17'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI483510',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_HEATER_NODE = 'true',
                    NEED_PAUSE_HEATER_NODE = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4835V11', 'P4835V12', 'P4850V13'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'ALPMAGW5DI483510'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'ALPMAGW5DI483511', 'ALPMAGW5DO483511' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4835V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4835V17'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 6 ] =
        {
        n          = 4840,
        tech_type  = 6,
        name       = 'Формовочная карусель MC-2000',
        name_eplan = 'P',
        name_BC    = 'P4840Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '10 16',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE2DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE2DI484004',
                    CIP_WASH_END = 'MCA5LINE2DI484005',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI484001',
                    NEED_COOLING = 'false',
                    NEED_HEATER_NODE = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4840V36', 'P4840V31', 'P4840V41'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE2DI1', 'ALPMAGW5DI484001'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE2DI484001', 'ALPMAGW5DO484001' }, 0, },
                            { { 'MCA5LINE2DI484002', 'ALPMAGW5DO484002' }, 0, },
                            { { 'MCA5LINE2DI484003', 'ALPMAGW5DO484003' }, 0, },
                            { { 'ALPMAGW5DI484001', 'MCA5LINE2DO484001' }, 0, },
                            { { 'ALPMAGW5DI484002', 'MCA5LINE2DO484002' }, 0, },
                            { { 'ALPMAGW5DI484003', 'MCA5LINE2DO484003' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'P4840V11', 'P4840V16', 'P4840V18', 'P4840V20', 'P4840V21', 'P4840V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V13', 'P4840V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI484002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4840V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = 18,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'P4840V11', 'P4840V16', 'P4840V18', 'P4840V20', 'P4840V21', 'P4840V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V12', 'P4840V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI484002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4840V13'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = 19,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4840V16', 'P4840V18', 'P4840V3', 'P4840V20', 'P4840V17', 'P4840V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V12', 'P4840V13', 'P4840V21'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE2DO484004', 'ALPMAGW5DO484006'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды ',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4840V11', 'P4840V16', 'P4840V18', 'P4840V20', 'P4840V21', 'P4840V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V12', 'P4840V13', 'P4840V3'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE2DI484004', 'ALPMAGW5DO484004' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4840V11', 'P4840V12', 'P4840V16', 'P4840V18', 'P4840V20', 'P4840V21', 'P4840V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V13', 'P4840V3'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4840V12', 'P4840V16', 'P4840V13', 'P4840V18'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V11', 'P4840V3', 'P4840V20', 'P4840V21', 'P4840V17', 'MCA5LINE2DO484001'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO484005'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4840V17', 'P4840V20'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI484010',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_COOLING = 'true',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_HEATER_NODE = 'true',
                    NEED_PAUSE_HEATER_NODE = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'P4875V43', 'P4850V43', 'P4870V43'
                            },
                        closed_devices = --Выключать
                            {
                            'P4840V11', 'P4840V12', 'P4840V13', 'P4840V21'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11', 'ALPMAGW5DI484010'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4840V16', 'P4840V18', 'P4840V3', 'P4840V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI484011'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4840V41'
                                            },
                                        },
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        on_devices = --Включение устройств
                                            {
                                            'ALPMAGW5DI484015'
                                            },
                                        next_step_n = 2, --Шаг
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Опорожнение в дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4840V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4840V17', 'P4840V20'
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        off_devices = --Выключение устройств
                                            {
                                            'ALPMAGW5DI484015'
                                            },
                                        next_step_n = 1, --Шаг
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 7 ] =
        {
        n          = 4850,
        tech_type  = 7,
        name       = 'Формовочная машина MD4-E',
        name_eplan = 'P',
        name_BC    = 'P4850Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '17',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE4DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE4DI485004',
                    CIP_WASH_END = 'MCA5LINE4DI485005',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI485001',
                    NEED_HEATER_NODE = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4850V36', 'P4850V41'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE4DI1', 'ALPMAGW5DI485001'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE4DI485001', 'ALPMAGW5DO485001' }, 0, },
                            { { 'MCA5LINE4DI485002', 'ALPMAGW5DO485002' }, 0, },
                            { { 'MCA5LINE4DI485003', 'ALPMAGW5DO485003' }, 0, },
                            { { 'ALPMAGW5DI485001', 'MCA5LINE4DO485001' }, 0, },
                            { { 'ALPMAGW5DI485002', 'MCA5LINE4DO485002' }, 0, },
                            { { 'ALPMAGW5DI485003', 'MCA5LINE4DO485003' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4850V11', 'P4850V16', 'P4850V17', 'P4850V13'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI485002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4850V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4850V11', 'P4850V16', 'P4850V17', 'P4850V13'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4850V12'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE4DI485004', 'ALPMAGW5DO485004' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4850V11', 'P4850V12', 'P4850V16', 'P4850V17', 'P4850V13'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4850V12', 'P4850V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4850V11', 'P4850V17', 'P4850V13', 'MCA5LINE4DO485001'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO485005'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4850V17'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI485010',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_HEATER_NODE = 'true',
                    NEED_PAUSE_HEATER_NODE = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'P4875V43'
                            },
                        closed_devices = --Выключать
                            {
                            'P4850V11', 'P4850V12', 'P4850V16'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11', 'ALPMAGW5DI485010'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI485011'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4850V41'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 8 ] =
        {
        n          = 4870,
        tech_type  = 8,
        name       = 'Охлаждающая ванна CV5-2',
        name_eplan = 'P',
        name_BC    = 'P4870Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '11',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 120,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE1DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE1DI487004',
                    CIP_WASH_END = 'MCA5LINE1DI487005',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI487001',
                    NEED_COOLING = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4870V31', 'P4870V41'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE1DI1', 'ALPMAGW5DI487001'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE1DI487001', 'ALPMAGW5DO487001' }, 0, },
                            { { 'MCA5LINE1DI487002', 'ALPMAGW5DO487002' }, 0, },
                            { { 'MCA5LINE1DI487003', 'ALPMAGW5DO487003' }, 0, },
                            { { 'ALPMAGW5DI487001', 'MCA5LINE1DO487001' }, 0, },
                            { { 'ALPMAGW5DI487002', 'MCA5LINE1DO487002' }, 0, },
                            { { 'ALPMAGW5DI487003', 'MCA5LINE1DO487003' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = 17,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'P4870V11', 'P4870V16', 'P4870V20', 'P4870V21', 'P4870V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4870V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI487002'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4870V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = 19,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4870V16', 'P4870V3', 'P4870V20', 'P4870V17', 'P4870V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4870V12', 'P4870V21'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE1DO487004', 'ALPMAGW5DO487006'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4870V11', 'P4870V16', 'P4870V20', 'P4870V21', 'P4870V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4870V12', 'P4870V3'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE1DI487004', 'ALPMAGW5DO487004' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4870V11', 'P4870V12', 'P4870V16', 'P4870V20', 'P4870V21', 'P4870V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4870V3'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4870V12', 'P4870V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4870V11', 'P4870V3', 'P4870V20', 'P4870V21', 'P4870V17', 'MCA5LINE1DO487001'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO487005'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4870V17', 'P4870V20'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI487010',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_COOLING = 'true',
                    NEED_PAUSE_COOLING = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'P4875V43', 'P4850V43'
                            },
                        closed_devices = --Выключать
                            {
                            'P4870V11', 'P4870V12', 'P4870V21'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11', 'ALPMAGW5DI487010'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'ALPMAGW5DO487010'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4870V16', 'P4870V3', 'P4870V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI487011'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4870V41'
                                            },
                                        },
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        on_devices = --Включение устройств
                                            {
                                            'ALPMAGW5DI487014'
                                            },
                                        next_step_n = 2, --Шаг
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Опорожнение в дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4870V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4870V3', 'P4870V20', 'P4870V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO487014'
                                            },
                                        },
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        off_devices = --Выключение устройств
                                            {
                                            'ALPMAGW5DI487014'
                                            },
                                        next_step_n = 1, --Шаг
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 9 ] =
        {
        n          = 4875,
        tech_type  = 9,
        name       = 'Охлаждающая ванна CV9-2',
        name_eplan = 'P',
        name_BC    = 'P4875Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '12',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 0,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE2DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE2DI487504',
                    CIP_WASH_END = 'MCA5LINE2DI487505',
                    CIP_WASH_REQUEST = 'ALPMAGW5DI487501',
                    NEED_COOLING = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4875V31', 'P4875V41'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE2DI1', 'ALPMAGW5DI487501'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE2DI487501', 'ALPMAGW5DO487501' }, 0, },
                            { { 'MCA5LINE2DI487502', 'ALPMAGW5DO487502' }, 0, },
                            { { 'MCA5LINE2DI487503', 'ALPMAGW5DO487503' }, 0, },
                            { { 'ALPMAGW5DI487501', 'MCA5LINE2DO487501' }, 0, },
                            { { 'ALPMAGW5DI487502', 'MCA5LINE2DO487502' }, 0, },
                            { { 'ALPMAGW5DI487503', 'MCA5LINE2DO487503' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'P4875V11', 'P4875V16', 'P4875V20', 'P4875V21', 'P4875V17', 'P4875V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V3', 'P4875V13'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI487502'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4875V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = 18,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'P4875V11', 'P4875V16', 'P4875V20', 'P4875V21', 'P4875V17', 'P4875V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V12', 'P4875V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI487502'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4875V13'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды',
                                time_param_n = 19,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4875V16', 'P4875V3', 'P4875V20', 'P4875V17', 'P4875V19', 'P4875V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V12', 'P4875V13', 'P4875V21'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE2DO487504', 'ALPMAGW5DO487506'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4875V11', 'P4875V16', 'P4875V20', 'P4875V21', 'P4875V17', 'P4875V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V3', 'P4875V12', 'P4875V13'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE2DI487504', 'ALPMAGW5DO487504' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4875V11', 'P4875V12', 'P4875V16', 'P4875V20', 'P4875V21', 'P4875V17', 'P4875V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V3', 'P4875V13'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4875V12', 'P4875V16', 'P4875V13', 'P4875V19'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V11', 'P4875V3', 'P4875V20', 'P4875V21', 'P4875V17', 'MCA5LINE2DO487501'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO487505'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4875V17', 'P4875V20'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI487510',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_COOLING = 'true',
                    NEED_PAUSE_COOLING = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4875V11', 'P4875V12', 'P4875V21', 'P4875V13', 'P4875V19'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11', 'ALPMAGW5DI487510'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'ALPMAGW5DO487510'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4875V16', 'P4875V3', 'P4875V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI487511'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4875V41'
                                            },
                                        },
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        on_devices = --Включение устройств
                                            {
                                            'ALPMAGW5DI487514'
                                            },
                                        next_step_n = 2, --Шаг
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Опорожнение в дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4875V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V3', 'P4875V20', 'P4875V17'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO487514'
                                            },
                                        },
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        off_devices = --Выключение устройств
                                            {
                                            'ALPMAGW5DI487514'
                                            },
                                        next_step_n = 1, --Шаг
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 10 ] =
        {
        n          = 4840,
        tech_type  = 14,
        name       = 'Охладитель Формовочная карусель MC-2000',
        name_eplan = 'P',
        name_BC    = 'P4840CoolObj1',
        cooper_param_number = -1,
        base_tech_object = 'cooler_node_PID',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура охлаждения продукта ',
                value = 5,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'COOL_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температуры охлаждения',
                value = 2,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'TE_COOL_DELTA'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        system_parameters =
            {
            P_k =
                {
                value = 1.2,
                },
            P_Ti =
                {
                value = 10,
                },
            P_Td =
                {
                value = 0.2,
                },
            P_dt =
                {
                value = 500,
                },
            P_max =
                {
                value = 100,
                },
            P_min =
                {
                value = 0,
                },
            P_acceleration_time =
                {
                value = 30,
                },
            P_is_manual_mode =
                {
                value = 0,
                },
            P_U_manual =
                {
                value = 65,
                },
            P_k2 =
                {
                value = 0,
                },
            P_Ti2 =
                {
                value = 0,
                },
            P_Td2 =
                {
                value = 0,
                },
            P_out_max =
                {
                value = 100,
                },
            P_out_min =
                {
                value = 0,
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Охлаждение',
                base_operation = 'COOLING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI484012',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4840V31'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO484012'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'P4840TE1',
            SET_VALUE = 'ALPMAGW5AI484011',
            VC = 'P4840VC1',
            },
        },
    [ 11 ] =
        {
        n          = 4870,
        tech_type  = 14,
        name       = 'Охладитель Охлаждающая ванна CV5-2',
        name_eplan = 'P',
        name_BC    = 'P4870CoolObj1',
        cooper_param_number = -1,
        base_tech_object = 'cooler_node_PID',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура охлаждения продукта ',
                value = 5,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'COOL_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температуры охлаждения',
                value = 2,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'TE_COOL_DELTA'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        system_parameters =
            {
            P_k =
                {
                value = 1.2,
                },
            P_Ti =
                {
                value = 10,
                },
            P_Td =
                {
                value = 0.2,
                },
            P_dt =
                {
                value = 500,
                },
            P_max =
                {
                value = 100,
                },
            P_min =
                {
                value = 0,
                },
            P_acceleration_time =
                {
                value = 30,
                },
            P_is_manual_mode =
                {
                value = 0,
                },
            P_U_manual =
                {
                value = 65,
                },
            P_k2 =
                {
                value = 0,
                },
            P_Ti2 =
                {
                value = 0,
                },
            P_Td2 =
                {
                value = 0,
                },
            P_out_max =
                {
                value = 100,
                },
            P_out_min =
                {
                value = 0,
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Охлаждение',
                base_operation = 'COOLING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI487012',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4870V31'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO487012'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'P4870TE1',
            SET_VALUE = 'ALPMAGW5AI487011',
            VC = 'P4870VC1',
            },
        },
    [ 12 ] =
        {
        n          = 4875,
        tech_type  = 14,
        name       = 'Охладитель Охлаждающая ванна CV9-2',
        name_eplan = 'P',
        name_BC    = 'P4875CoolObj1',
        cooper_param_number = -1,
        base_tech_object = 'cooler_node_PID',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура охлаждения продукта ',
                value = 5,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'COOL_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температуры охлаждения',
                value = 2,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'TE_COOL_DELTA'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        system_parameters =
            {
            P_k =
                {
                value = 1.2,
                },
            P_Ti =
                {
                value = 10,
                },
            P_Td =
                {
                value = 0.2,
                },
            P_dt =
                {
                value = 500,
                },
            P_max =
                {
                value = 100,
                },
            P_min =
                {
                value = 0,
                },
            P_acceleration_time =
                {
                value = 30,
                },
            P_is_manual_mode =
                {
                value = 0,
                },
            P_U_manual =
                {
                value = 65,
                },
            P_k2 =
                {
                value = 0,
                },
            P_Ti2 =
                {
                value = 0,
                },
            P_Td2 =
                {
                value = 0,
                },
            P_out_max =
                {
                value = 100,
                },
            P_out_min =
                {
                value = 0,
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Охлаждение',
                base_operation = 'COOLING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI487512',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4875V31'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO487512'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'P4875TE1',
            SET_VALUE = 'ALPMAGW5AI487511',
            VC = 'P4875VC1',
            },
        },
    [ 13 ] =
        {
        n          = 4885,
        tech_type  = 14,
        name       = 'Охладитель Формовочная карусель MC-2000',
        name_eplan = 'P',
        name_BC    = 'P4885CoolObj1',
        cooper_param_number = -1,
        base_tech_object = 'cooler_node_PID',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура охлаждения продукта ',
                value = 5,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'COOL_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температуры охлаждения',
                value = 2,
                meter = 'град.C',
                oper = { 1 },
                nameLua = 'TE_COOL_DELTA'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        system_parameters =
            {
            P_k =
                {
                value = 1.2,
                },
            P_Ti =
                {
                value = 10,
                },
            P_Td =
                {
                value = 0.2,
                },
            P_dt =
                {
                value = 500,
                },
            P_max =
                {
                value = 100,
                },
            P_min =
                {
                value = 0,
                },
            P_acceleration_time =
                {
                value = 30,
                },
            P_is_manual_mode =
                {
                value = 0,
                },
            P_U_manual =
                {
                value = 65,
                },
            P_k2 =
                {
                value = 0,
                },
            P_Ti2 =
                {
                value = 0,
                },
            P_Td2 =
                {
                value = 0,
                },
            P_out_max =
                {
                value = 100,
                },
            P_out_min =
                {
                value = 0,
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Охлаждение',
                base_operation = 'COOLING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI488512',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4885V31'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO488512'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'P4885TE1',
            SET_VALUE = 'ALPMAGW5AI488511',
            VC = 'P4885VC1',
            },
        },
    [ 14 ] =
        {
        n          = 4820,
        tech_type  = 15,
        name       = 'Узел нагревания Машина варки и вытяжки WCSLE-2000/A',
        name_eplan = 'P',
        name_BC    = 'P4820HeatObj1',
        cooper_param_number = -1,
        base_tech_object = 'heater_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Нагревание',
                base_operation = 'HEATING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI482014',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4820V36', 'P4820V37'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO482014'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = '',
            },
        },
    [ 15 ] =
        {
        n          = 4835,
        tech_type  = 15,
        name       = 'Узел нагревания Машина сухой посолки DS-1',
        name_eplan = 'P',
        name_BC    = 'P4835HeatObj1',
        cooper_param_number = -1,
        base_tech_object = 'heater_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Нагревание',
                base_operation = 'HEATING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI483514',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4835V36'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO483514'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = '',
            },
        },
    [ 16 ] =
        {
        n          = 4840,
        tech_type  = 15,
        name       = 'Узел нагревания Формовочная карусель MC-2000',
        name_eplan = 'P',
        name_BC    = 'P4840HeatObj1',
        cooper_param_number = -1,
        base_tech_object = 'heater_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Нагревание',
                base_operation = 'HEATING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI484014',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4840V36'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO484014'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = '',
            },
        },
    [ 17 ] =
        {
        n          = 4850,
        tech_type  = 15,
        name       = 'Узел нагревания Формовочная машина MD4-E',
        name_eplan = 'P',
        name_BC    = 'P4850HeatObj1',
        cooper_param_number = -1,
        base_tech_object = 'heater_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Нагревание',
                base_operation = 'HEATING',
                props =
                    {
                    WORK_REQUEST = 'ALPMAGW5DI485014',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_TO_WORK_REQUEST',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'P4850V36'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO485014'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = '',
            },
        },
    [ 18 ] =
        {
        n          = 7,
        tech_type  = 16,
        name       = 'Линия наполнения ALPMA O',
        name_eplan = 'O',
        name_BC    = 'O7LineInObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_in',
        attached_objects = '41',
        tank_groups =
            {
                tanks = '20',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время мойки основной линии',
                value = 600,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH'
                },
            [ 4 ] =
                {
                name = 'Время промывки седел клапанов',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_SED'
                },
            [ 5 ] =
                {
                name = 'Время промывки дренажа',
                value = 2,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_DRAINAGE'
                },
            [ 6 ] =
                {
                name = 'Время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_DRAINAGE'
                },
            [ 7 ] =
                {
                name = 'Флаг использования бачка лимонной кислоты',
                value = 0,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'ACTIVITY_TANK'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 10 ] =
                {
                name = 'Текущий приемник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_DESTINATION'
                },
            [ 11 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'WATER_FLAG'
                },
            [ 12 ] =
                {
                name = 'Принятый объем продукта',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 13 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Электропроводность основы',
                value = 3,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'CONCENTRATION'
                },
            [ 16 ] =
                {
                name = 'Дельта электропроводности основы',
                value = 0.2,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'D_CONCENTRATION'
                },
            [ 17 ] =
                {
                name = 'Время отсутствия расхода для завершения наполнения',
                value = 60,
                meter = 'с',
                oper = { 2 },
                nameLua = 'NO_FLOW_TIME'
                },
            [ 18 ] =
                {
                name = 'Минимальный расход для завершения дренажа',
                value = 0.4,
                meter = 'м куб./ч',
                oper = { 2 },
                nameLua = 'MIN_FLOW'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_END = 'O7DI2',
                    IGNORE_WATER_FLAG = 'false',
                    NEED_FLOW_CONTROL = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'LA_TANK1V101'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BERTSCH_MOZ_GW1DI1'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'UF1_O7DI2', 'O7DO2' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 3,
                                next_step_n = 2,
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI1', 'UF1_O7DO1' }, 0, },
                                    { { 'UF1_O7DI1', 'O7DO1' }, 0, },
                                    { { 'O7DI1', 'BERTSCH_MOZ_GW1DO1' }, 0, },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Промывка седел',
                                time_param_n = 4,
                                next_step_n = 3,
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'LA_TANK1V101'
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI1', 'UF1_O7DO1' }, 0, },
                                    { { 'UF1_O7DI1', 'O7DO1' }, 0, },
                                    { { 'O7DI1', 'BERTSCH_MOZ_GW1DO1' }, 0, },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Промывка дренажа',
                                time_param_n = 5,
                                next_step_n = 1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'O7DO2'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI1', 'UF1_O7DO1' }, 0, },
                                    { { 'UF1_O7DI1', 'O7DO1' }, 0, },
                                    { { 'O7DI1', 'BERTSCH_MOZ_GW1DO1' }, 0, },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 6,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'UF1_O7DO2'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    TOTAL_VOLUME_AI = 'O7AI13',
                    CONCENTRATION = 'CONCENTRATION',
                    DELTA_CONCENTRATION = 'D_CONCENTRATION',
                    IS_END_ON_FULL_TANK = 'false',
                    MOVE_TO_STEP_WAITING_BY_SIGNALS = 'false',
                    NEED_PAUSE_AFTER_FULL_LAST_TANK = 'false',
                    CONTINUE_PRODUCT_PUSH = 'true',
                    NEED_FLOW_CONTROL = 'true',
                    NEED_PAUSE_FLOW_CONTROL = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        checked_devices = --Проверяемые устройства
                            {
                            'O7FQT1'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'UF1_O7DO11'
                                    },
                                },
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'UF1_O7DI11', 'O7DO11' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_KEY',
                                },
                            [ 2 ] =
                                {
                                name = 'В дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_DRAINAGE',
                                },
                            [ 3 ] =
                                {
                                name = 'В танк №1',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_TANK',
                                },
                            [ 4 ] =
                                {
                                name = 'В танк №2 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 5 ] =
                                {
                                name = 'В танк №3 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 6 ] =
                                {
                                name = 'В танк №4 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 7 ] =
                                {
                                name = 'В танк №5 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 8 ] =
                                {
                                name = 'Запрос проталкивания',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'PRODUCT_PUSH',
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'O7DO12'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Наполнение в Ультрафильтрации',
                },
            },
        equipment =
            {
            QT = 'O7QT1',
            product_CTR = 'O7FQT1',
            },
        },
    [ 19 ] =
        {
        n          = 4885,
        tech_type  = 10,
        name       = 'Солильная ванна BV 29-2.2',
        name_eplan = 'P',
        name_BC    = 'P4885Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '13',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "Основная зона"',
                value = 90,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Вспомогательная зона"',
                value = 90,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 1"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE_1'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Зона технолог./охлажд. воды 2"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE_2'
                },
            [ 21 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE3DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE3DI488504',
                    CIP_WASH_END = 'MCA5LINE3DI488505',
                    NEED_COOLING = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4885V31'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE3DI1', 'ALPMAGW5DI488501'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'MCA5LINE3DI488501', 'ALPMAGW5DO488501' }, 0, },
                            { { 'MCA5LINE3DI488502', 'ALPMAGW5DO488502' }, 0, },
                            { { 'MCA5LINE3DI488503', 'ALPMAGW5DO488503' }, 0, },
                            { { 'ALPMAGW5DI488501', 'MCA5LINE3DO488501' }, 0, },
                            { { 'ALPMAGW5DI488502', 'MCA5LINE3DO488502' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Основная зона',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'P4885V11', 'P4885V16', 'P4885V21', 'P4885V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V3', 'P4885V13', 'P4885V20'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488502'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4885V12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Вспомогательная зона',
                                time_param_n = 18,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'P4885V11', 'P4885V16', 'P4885V21', 'P4885V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V12', 'P4885V3', 'P4885V20'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488502'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4885V13'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Зона технолог./охлажд. воды 1',
                                time_param_n = 19,
                                next_step_n = 4,
                                opened_devices = --Включать
                                    {
                                    'P4885V16', 'P4885V3', 'P4885V17', 'P4885V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V12', 'P4885V13', 'P4885V21', 'P4885V20'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE3DO488504', 'ALPMAGW5DO488506'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Зона технолог./охлажд. воды 2',
                                time_param_n = 20,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4885V16', 'P4885V3', 'P4885V17', 'P4885V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V12', 'P4885V13', 'P4885V21', 'P4885V20'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE3DO488504', 'ALPMAGW5DO488507'
                                            },
                                        },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'P4885V11', 'P4885V16', 'P4885V21', 'P4885V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V3', 'P4885V12', 'P4885V13', 'P4885V20'
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'MCA5LINE3DI488504', 'ALPMAGW5DO488504' }, 0, },
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 21,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'P4885V11', 'P4885V12', 'P4885V16', 'P4885V21', 'P4885V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V3', 'P4885V13', 'P4885V20'
                                    },
                                },
                            [ 7 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4885V12', 'P4885V16', 'P4885V13', 'P4885V20'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V11', 'P4885V3', 'P4885V21', 'P4885V17', 'MCA5LINE3DO488501'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO488505'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4885V17'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Производство',
                base_operation = 'WORK',
                props =
                    {
                    AUTO_DI = 'ALPMAGW5DI488510',
                    WORK_FILL_AND_OUT = 'false',
                    NEED_COOLING = 'true',
                    NEED_PAUSE_COOLING = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4885V11', 'P4885V12', 'P4885V21', 'P4885V13'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'ALPMAGW5DI488510'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4885V16', 'P4885V17'
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        on_devices = --Включение устройств
                                            {
                                            'ALPMAGW5DI488514'
                                            },
                                        next_step_n = 2, --Шаг
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Опорожнение',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4885V16', 'P4885V17'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4885V20'
                                    },
                                jump_if = --Переход к следующему шагу по условию
                                    {
                                    --Группа
                                        {
                                        off_devices = --Выключение устройств
                                            {
                                            'ALPMAGW5DI488514'
                                            },
                                        next_step_n = 1, --Шаг
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'P4885V17'
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 20 ] =
        {
        n          = 1,
        tech_type  = 11,
        name       = 'Сыроизготовитель (Резерв)',
        name_eplan = 'COAG',
        name_BC    = 'Coag1Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Тип продукта',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'PRODUCT_TYPE'
                },
            [ 4 ] =
                {
                name = 'Номер линии наполнения',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'IN_LINE_OBJ_NUMBER'
                },
            [ 5 ] =
                {
                name = 'Номер линии выдачи',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'OUT_LINE_OBJ_NUMBER'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 0,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Номер партии в танке',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'PART_NUMB1'
                },
            [ 8 ] =
                {
                name = 'Дата (день) производства партии в танке',
                value = 0,
                meter = 'д',
                oper = { -1 },
                nameLua = 'PART_DAY1'
                },
            [ 9 ] =
                {
                name = 'Дата (месяц) производства партии в танке',
                value = 0,
                meter = 'мес',
                oper = { -1 },
                nameLua = 'PART_MONTH1'
                },
            [ 10 ] =
                {
                name = 'Дата (год) производства партии в танке',
                value = 0,
                meter = 'г',
                oper = { -1 },
                nameLua = 'PART_YEAR1'
                },
            [ 11 ] =
                {
                name = 'Текущий набранный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_CURRENT'
                },
            [ 12 ] =
                {
                name = 'Заданный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_SET'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "В танк"',
                value = 150,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_TANK_TIME'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Флипование"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_FLUSH_TIME'
                },
            [ 19 ] =
                {
                name = 'Время дренажа после пропадания НУ',
                value = 300,
                meter = 'с',
                oper = { -1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 20 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 21 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 22 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 26 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 27 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 28 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 29 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 30 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 31 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 32 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 33 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 34 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 35 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 36 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 37 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 38 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 39 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 40 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 41 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 42 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 43 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 44 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 45 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 46 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 47 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 48 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 49 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 50 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE1DI1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'В танк',
                                time_param_n = 17,
                                next_step_n = 2,
                                },
                            [ 2 ] =
                                {
                                name = 'Флипование',
                                time_param_n = 18,
                                next_step_n = 1,
                                },
                            [ 3 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 20,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                },
            [ 3 ] =
                {
                name = 'Нагрев',
                },
            [ 4 ] =
                {
                name = 'Откачка сыворотки',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        required_FB = --Сигналы для включения
                            {
                            'W2DI11'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'W2DO11'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = '',
            hatch = '',
            hatch2 = '',
            LS_down = '',
            LT = '',
            TE = '',
            lamp = '',
            },
        },
    [ 21 ] =
        {
        n          = 1,
        tech_type  = 12,
        name       = 'Бачок лимонной кислоты',
        name_eplan = 'LA_TANK',
        name_BC    = 'LATank1Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '23',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Тип продукта',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'PRODUCT_TYPE'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Номер партии в танке',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'PART_NUMB1'
                },
            [ 8 ] =
                {
                name = 'Дата (день) производства партии в танке',
                value = 0,
                meter = 'д',
                oper = { -1 },
                nameLua = 'PART_DAY1'
                },
            [ 9 ] =
                {
                name = 'Дата (месяц) производства партии в танке',
                value = 0,
                meter = 'мес',
                oper = { -1 },
                nameLua = 'PART_MONTH1'
                },
            [ 10 ] =
                {
                name = 'Дата (год) производства партии в танке',
                value = 0,
                meter = 'г',
                oper = { -1 },
                nameLua = 'PART_YEAR1'
                },
            [ 11 ] =
                {
                name = 'Текущий набранный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_CURRENT'
                },
            [ 12 ] =
                {
                name = 'Заданный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_SET'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Максимальный уровень для включения мойки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_MAX_LT'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "В танк"',
                value = 150,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_TANK_TIME'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Флипование"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_FLUSH_TIME'
                },
            [ 19 ] =
                {
                name = 'Время дренажа после пропадания НУ',
                value = 180,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 20 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 21 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 22 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 23 ] =
                {
                name = 'Минимальный уровень для работы мешалки',
                value = 10,
                meter = '%',
                oper = { 2,3,4 },
                nameLua = 'MIX_MIN_LT'
                },
            [ 24 ] =
                {
                name = 'Дельта мин. уровня для включения мешалки',
                value = 1,
                meter = '%',
                oper = { 2,3,4 },
                nameLua = 'MIX_DELTA_LT'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 26 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 27 ] =
                {
                name = 'Время работы мешалки',
                value = 0,
                meter = 'мин',
                oper = { -1 },
                nameLua = 'MIX_TIME_ON'
                },
            [ 28 ] =
                {
                name = 'Время простоя мешалки',
                value = 0,
                meter = 'мин',
                oper = { -1 },
                nameLua = 'MIX_TIME_OFF'
                },
            [ 29 ] =
                {
                name = 'Время работы мешалки при наполнении',
                value = 5,
                meter = 'мин',
                oper = { 2 },
                nameLua = 'FILL_MIX_TIME_ON'
                },
            [ 30 ] =
                {
                name = 'Время простоя мешалки при наполнении',
                value = 1,
                meter = 'мин',
                oper = { 2 },
                nameLua = 'FILL_MIX_TIME_OFF'
                },
            [ 31 ] =
                {
                name = 'Время работы мешалки при хранении',
                value = 15,
                meter = 'мин',
                oper = { 3 },
                nameLua = 'STORE_MIX_ON_PHASE1_TIME'
                },
            [ 32 ] =
                {
                name = 'Время простоя мешалки при хранении',
                value = 15,
                meter = 'мин',
                oper = { 3 },
                nameLua = 'STORE_MIX_WAIT_PHASE1_TIME'
                },
            [ 33 ] =
                {
                name = 'Время работы мешалки при выдаче',
                value = 15,
                meter = 'мин',
                oper = { 4 },
                nameLua = 'OUT_MIX_ON_PHASE1_TIME'
                },
            [ 34 ] =
                {
                name = 'Время простоя мешалки при выдаче',
                value = 15,
                meter = 'мин',
                oper = { 4 },
                nameLua = 'OUT_MIX_WAIT_PHASE1_TIME'
                },
            [ 35 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 36 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 37 ] =
                {
                name = 'Производительность мешалки во время мойки',
                value = 20,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_MIX_SPEED'
                },
            [ 38 ] =
                {
                name = 'Производительность мешалки во время наполнения',
                value = 100,
                meter = '%',
                oper = { 2 },
                nameLua = 'FILL_MIX_SPEED'
                },
            [ 39 ] =
                {
                name = 'Производительность мешалки во время хранения',
                value = 50,
                meter = '%',
                oper = { 3 },
                nameLua = 'STORING_MIX_SPEED'
                },
            [ 40 ] =
                {
                name = 'Производительность мешалки во время выдачи',
                value = 50,
                meter = '%',
                oper = { 4 },
                nameLua = 'OUT_MIX_SPEED'
                },
            [ 41 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 42 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 43 ] =
                {
                name = 'Концентрация раствора лимонной кислоты',
                value = 26,
                meter = '%',
                oper = { 4 },
                nameLua = 'CONC_SOLUTION'
                },
            [ 44 ] =
                {
                name = 'Заданная концентрация лимонной кислоты в смеси',
                value = 0.12,
                meter = '%',
                oper = { 4 },
                nameLua = 'SP_CONC_MIXTURE'
                },
            [ 45 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 46 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 47 ] =
                {
                name = 'Задержка выключения выдачи по НУ',
                value = 20,
                meter = 'с',
                oper = { 4 },
                nameLua = 'DELAY_OUT_OFF_TIME'
                },
            [ 48 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 49 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 50 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA4LINE3DI21',
                    CIP_WASH_END = 'MCA4LINE3DI23',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'WASH_MIX_SPEED',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'LA_TANK1V1', 'LA_TANK1V13'
                            },
                        closed_devices = --Выключать
                            {
                            'LA_TANK1V2'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA4LINE3DI21'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DI = --DI
                                    {
                                    'MCA4LINE3DI22'
                                    },
                                DO = --DO
                                    {
                                    'MCA4LINE3DO21'
                                    },
                                devices = --Устройства
                                    {
                                    'LA_TANK1M2'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'В танк',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1V12', 'LA_TANK1V11', 'CIPV7', 'LA_TANK1V4'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'LA_TANK1V14', 'LA_TANK1V18'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Флипование',
                                time_param_n = 18,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1V14', 'LA_TANK1V3', 'LA_TANK1V11', 'LA_TANK1V12', 'CIPV7'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'LA_TANK1V18', 'LA_TANK1V4'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'LA_TANK1V101'
                                        },
                                     --Группа
                                        {
                                        'LA_TANK1V102'
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 20,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1V14', 'LA_TANK1V3', 'LA_TANK1V4', 'LA_TANK1V18'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'LA_TANK1V11', 'LA_TANK1V12', 'CIPV7'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'FILL_MIX_SPEED',
                    MIX_NODE_MIX_ON_TIME = 'FILL_MIX_TIME_ON',
                    MIX_NODE_MIX_OFF_TIME = 'FILL_MIX_TIME_OFF',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'LA_TANK1V1', 'LA_TANK1V2', 'LA_TANK1V3', 'LA_TANK1V14', 'LA_TANK1V13', 'LA_TANK1V101', 'LA_TANK1V4', 'LA_TANK1V18'
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Хранение',
                base_operation = 'STORING',
                props =
                    {
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'STORING_MIX_SPEED',
                    MIX_NODE_MIX_ON_TIME = 'STORE_MIX_ON_PHASE1_TIME',
                    MIX_NODE_MIX_OFF_TIME = 'STORE_MIX_WAIT_PHASE1_TIME',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'LA_TANK1V1', 'LA_TANK1V2', 'LA_TANK1V3', 'LA_TANK1V14', 'LA_TANK1V13', 'LA_TANK1V101', 'LA_TANK1V4', 'LA_TANK1V18'
                            },
                        },
                    },
                },
            [ 4 ] =
                {
                name = 'Выдача',
                base_operation = 'OUT',
                props =
                    {
                    NEED_STORING_AFTER = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'FILL_MIX_SPEED',
                    MIX_NODE_MIX_ON_TIME = 'FILL_MIX_TIME_ON',
                    MIX_NODE_MIX_OFF_TIME = 'FILL_MIX_TIME_OFF',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Выдача в O7',
                                time_param_n = -1,
                                next_step_n = -1,
                                checked_devices = --Проверяемые устройства
                                    {
                                    'LA_TANK1FQT1'
                                    },
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1V2', 'LA_TANK1V101', 'LA_TANK1M3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'LA_TANK1V1', 'LA_TANK1V3', 'LA_TANK1V14', 'LA_TANK1V13', 'LA_TANK1V4', 'LA_TANK1V18', 'LA_TANK1V102'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Выдача в O8',
                                time_param_n = -1,
                                next_step_n = -1,
                                checked_devices = --Проверяемые устройства
                                    {
                                    'LA_TANK1FQT1'
                                    },
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1V2', 'LA_TANK1V102', 'LA_TANK1M3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'LA_TANK1V1', 'LA_TANK1V3', 'LA_TANK1V14', 'LA_TANK1V13', 'LA_TANK1V4', 'LA_TANK1V18', 'LA_TANK1V101'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = 'LA_TANK1LS2',
            hatch = '',
            hatch2 = '',
            LS_down = 'LA_TANK1LS1',
            LT = 'LA_TANK1LT1',
            TE = 'LA_TANK1TE1',
            lamp = '',
            out_pump = 'LA_TANK1M2',
            },
        },
    [ 22 ] =
        {
        n          = 1,
        tech_type  = 13,
        name       = 'Танк рассола',
        name_eplan = 'BRINE_TANK',
        name_BC    = 'BrineTank1Obj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Ожидание уровня для откачки после ВУ',
                value = 18,
                meter = '%',
                oper = { 3 },
                nameLua = 'HIGH_LEVEL_WAIT_PUMP_OUT'
                },
            [ 15 ] =
                {
                name = 'Ожидание уровня для откачки',
                value = 2,
                meter = '%',
                oper = { 2,3 },
                nameLua = 'LEVEL_WAIT_PUMP_OUT'
                },
            [ 16 ] =
                {
                name = 'Максимальный уровень для включения мойки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_MAX_LT'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "На МГ"',
                value = 120,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_MAIN_ZONE'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Линия наполнения"',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_AUX_ZONE'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Линия возврата"',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_WATER_ZONE'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 15,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 21 ] =
                {
                name = 'Время дренажа после пропадания НУ',
                value = 180,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Производительность насоса во время мойки',
                value = 80,
                meter = '%',
                oper = { 1 },
                nameLua = 'POWER_PUMP_CIP'
                },
            [ 24 ] =
                {
                name = 'Производительность насоса во время наполнения',
                value = 40,
                meter = '%',
                oper = { 2 },
                nameLua = 'POWER_PUMP_FILL'
                },
            [ 25 ] =
                {
                name = 'Производительность насоса во время циркуляции',
                value = 37,
                meter = '%',
                oper = { 3 },
                nameLua = 'POWER_PUMP_CIRCULATION'
                },
            [ 26 ] =
                {
                name = 'Производительность насоса во время откачки',
                value = 80,
                meter = '%',
                oper = { 4 },
                nameLua = 'POWER_PUMP_EMPTYING'
                },
            [ 27 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 28 ] =
                {
                name = 'Задержка выключения выдачи по НУ',
                value = 20,
                meter = 'с',
                oper = { 2,4 },
                nameLua = 'DELAY_OUT_OFF_TIME'
                },
            [ 29 ] =
                {
                name = 'Время работы шагов завершения работы с MF2',
                value = 5,
                meter = 'с',
                oper = { 3 },
                nameLua = 'TIME_RUNNING_END_STEPS_MF2'
                },
            [ 30 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 31 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 32 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 33 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 34 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 35 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE3DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE3DI488504',
                    CIP_WASH_END = 'MCA5LINE3DI488505',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'BRINE_TANK1V21', 'BRINE_TANK1V22'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE3DI1', 'ALPMAGW5DI488501'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DI = --DI
                                    {
                                    'MCA5LINE3DI488503'
                                    },
                                devices = --Устройства
                                    {
                                    'BRINE_TANK1M1'
                                    },
                                pump_freq = 'POWER_PUMP_CIP',
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'На МГ',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V2', 'BRINE_TANK1V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V12', 'BRINE_TANK1V13'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Линия наполнения',
                                time_param_n = 18,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V2', 'BRINE_TANK1V11', 'BRINE_TANK1V13'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V12'
                                    },
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'BRINE_TANK1V21'
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Линия возврата',
                                time_param_n = 19,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V2', 'BRINE_TANK1V12'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V11', 'BRINE_TANK1V13'
                                    },
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'BRINE_TANK1V22'
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V11', 'BRINE_TANK1V12', 'BRINE_TANK1V13', 'BRINE_TANK1V1', 'BRINE_TANK1V2'
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 20,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V2', 'BRINE_TANK1V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V12', 'BRINE_TANK1V13'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE3DO488503'
                                            },
                                        },
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V11', 'BRINE_TANK1V12', 'BRINE_TANK1V13'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V2'
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V2'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение в 4885',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'BRINE_TANK1V13', 'BRINE_TANK1V14', 'BRINE_TANK1V11', 'BRINE_TANK1V15'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'ALPMAGW5DI488511'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'BRN3DO11', 'BRN3DO13'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Заполнение линии циркуляции',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V14', 'BRINE_TANK1V15'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V21', 'BRINE_TANK1V22'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN3DO12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Ожидание появления уровня',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V21', 'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1M1'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN3DO12'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Откачка до НУ',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V21', 'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488516'
                                            },
                                        DO = --DO
                                            {
                                            'BRN3DO12', 'ALPMAGW5DO488511'
                                            },
                                        devices = --Устройства
                                            {
                                            'BRINE_TANK1M1'
                                            },
                                        pump_freq = 'POWER_PUMP_FILL',
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Появление ВУ',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V21'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488516'
                                            },
                                        DO = --DO
                                            {
                                            'ALPMAGW5DO488511'
                                            },
                                        devices = --Устройства
                                            {
                                            'BRINE_TANK1M1'
                                            },
                                        pump_freq = 'POWER_PUMP_FILL',
                                        },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Полное опустошение',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V21', 'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488516'
                                            },
                                        DO = --DO
                                            {
                                            'BRN3DO12', 'ALPMAGW5DO488511'
                                            },
                                        devices = --Устройства
                                            {
                                            'BRINE_TANK1M1'
                                            },
                                        pump_freq = 'POWER_PUMP_FILL',
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V2'
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Циркуляция через 4885',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'BRINE_TANK1V13', 'BRINE_TANK1V14', 'BRINE_TANK1V11', 'BRINE_TANK1V15'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'ALPMAGW5DI488513'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'ALPMAGW5DO488513'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание появления уровня',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4885V16', 'P4885V17', 'BRINE_TANK1V12', 'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1M1'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Откачка до НУ',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4885V16', 'P4885V17', 'BRINE_TANK1V12', 'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488516'
                                            },
                                        devices = --Устройства
                                            {
                                            'BRINE_TANK1M1'
                                            },
                                        pump_freq = 'ALPMAGW5AI488513',
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Опустошение после появления ВУ',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1V2', 'P4885V3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V12'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488516'
                                            },
                                        devices = --Устройства
                                            {
                                            'BRINE_TANK1M1'
                                            },
                                        pump_freq = 'ALPMAGW5AI488513',
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Циркуляция через MF2 (Alpma)',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V21', 'BRINE_TANK1V22'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN3DO15'
                                            },
                                        },
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN3DO112', 'BRN3DO113', 'BRN3DO122', 'BRN3DO123', 'BRN3DO124'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BRN3DI114', 'BRN3DO114' }, 0, },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Завершение подачи на MF2 (Alpma)',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRN3DO115'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V22'
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Завершение выдачи из MF2 (Alpma)',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRN3DO125'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V21'
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V2'
                            },
                        },
                    },
                },
            [ 4 ] =
                {
                name = 'Откачка из 4885',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V2'
                            },
                        closed_devices = --Выключать
                            {
                            'BRINE_TANK1V13', 'BRINE_TANK1V11', 'BRINE_TANK1V12', 'BRINE_TANK1V21'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'BRN3DI11', 'ALPMAGW5DO488514' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Откачка в 4885',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V1', 'P4885V3', 'BRINE_TANK1V22'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V14', 'BRINE_TANK1V15'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI488516'
                                            },
                                        devices = --Устройства
                                            {
                                            'BRINE_TANK1M1'
                                            },
                                        pump_freq = 'POWER_PUMP_EMPTYING',
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Откачка из 4885',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V22'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V1', 'BRINE_TANK1M1', 'BRINE_TANK1V14', 'BRINE_TANK1V15'
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Проталкивание линии циркуляции',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRINE_TANK1V14', 'BRINE_TANK1V15'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRINE_TANK1V21', 'BRINE_TANK1V22', 'BRINE_TANK1V1'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN3DO14'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = 'BRINE_TANK1LS2',
            hatch = 'BRINE_TANK1GS1',
            hatch2 = '',
            LS_down = 'BRINE_TANK1LS1',
            LT = 'BRINE_TANK1LT1',
            TE = 'BRINE_TANK1TE1',
            lamp = '',
            out_pump = 'BRINE_TANK1M1',
            },
        },
    [ 23 ] =
        {
        n          = 1,
        tech_type  = 18,
        name       = 'Узел перемешивания Бачок лим. кисл.',
        name_eplan = 'LA_TANK',
        name_BC    = 'LATank1MIXObj1',
        cooper_param_number = -1,
        base_tech_object = 'mix_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время работы мешалки при перемешивании',
                value = 1,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'MIX_TIME_ON'
                },
            [ 4 ] =
                {
                name = 'Время простоя мешалки при перемешивании',
                value = 10,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'MIX_TIME_OFF'
                },
            [ 5 ] =
                {
                name = 'Время перемешивания',
                value = 600,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'TOTAL_MIX_TIME'
                },
            [ 6 ] =
                {
                name = 'Производительность мешалки',
                value = 50,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_SPEED'
                },
            [ 7 ] =
                {
                name = 'Минимальный уровень для работы мешалки',
                value = 10,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_MIN_LT'
                },
            [ 8 ] =
                {
                name = 'Дельта мин. уровня для включения мешалки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_DELTA_LT'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Перемешивание',
                base_operation = 'MIXING',
                props =
                    {
                    WORK_WITH_SECTIONS = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа мешалки',
                                time_param_n = 3,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1M1'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Простой мешалки',
                                time_param_n = 4,
                                next_step_n = 1,
                                closed_devices = --Выключать
                                    {
                                    'LA_TANK1M1'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            hatch = '',
            bar = '',
            LT = 'LA_TANK1LT1',
            mix = 'LA_TANK1M1',
            },
        },
    [ 24 ] =
        {
        n          = 1,
        tech_type  = 19,
        name       = 'Узел подогрева Сыроизготовитель(Резерв)',
        name_eplan = 'COAG',
        name_BC    = 'Coag1HeatObj1',
        cooper_param_number = -1,
        base_tech_object = 'user_object',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Нагрев',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание сигнала запроса работы',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        },
    [ 25 ] =
        {
        n          = 1,
        tech_type  = 17,
        name       = 'Бачок откачки сыворотки (Резерв)',
        name_eplan = '',
        name_BC    = '',
        cooper_param_number = -1,
        base_tech_object = 'user_object',

        modes =
            {
            },
        },
    [ 26 ] =
        {
        n          = 1,
        tech_type  = 20,
        name       = 'Бункер фасовки PFM',
        name_eplan = 'BUNKER',
        name_BC    = 'BunkerObj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "PFM+л.циркуляции"',
                value = 90,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_PFM_LINE_TIME'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "PFM"',
                value = 30,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_PFM_TIME'
                },
            [ 19 ] =
                {
                name = 'Время шага мойки "Промывка трубы"',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_FLUSH_TIME'
                },
            [ 20 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 5,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY'
                },
            [ 21 ] =
                {
                name = 'Время дренажа после пропадания НУ',
                value = 120,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 22 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 23 ] =
                {
                name = 'Производительность насоса во время мойки',
                value = 80,
                meter = '%',
                oper = { 1 },
                nameLua = 'POWER_PUMP_CIP'
                },
            [ 24 ] =
                {
                name = 'Производительность насоса во время выдачи',
                value = 60,
                meter = '%',
                oper = { 2 },
                nameLua = 'POWER_PUMP_WORK'
                },
            [ 25 ] =
                {
                name = 'Заданный объем',
                value = 30,
                meter = '%',
                oper = { 2 },
                nameLua = 'V_LT_SET'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE4DI1',
                    MEDIUM_CHANGE_REQUEST = 'MCA5LINE4DI4',
                    CIP_WASH_END = 'MCA5LINE4DI3',
                    CIP_WASH_REQUEST = 'PFM1DI1',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'BUNKER1V21', 'BUNKER1V22', 'BUNKER1V23', 'BUNKER1V24', 'BUNKER1V25', 'BUNKER1V26', 'BUNKER1V27'
                            },
                        closed_devices = --Выключать
                            {
                            'BUNKER1V40', 'CIPV1', 'F_BRINE_OUT1V4', 'F_BRINE_OUT1V3', 'BUNKER1V6'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE4DI1', 'PFM1DI1'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DI = --DI
                                    {
                                    'MCA5LINE4DI2'
                                    },
                                DO = --DO
                                    {
                                    'MCA5LINE4DO3', 'PFM1DO1'
                                    },
                                devices = --Устройства
                                    {
                                    'BUNKER1M1'
                                    },
                                pump_freq = 'POWER_PUMP_CIP',
                                },
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'PFM1DI2', 'PFM1DO2' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка PFM+л.циркуляции',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V11', 'BUNKER1V13', 'BUNKER1V15', 'BUNKER1V1', 'BUNKER1V16', 'BUNKER1V17', 'CIPV3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V2', 'BUNKER1V5', 'BUNKER1V14'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'F_BRINE_OUT1V3'
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Мойка PFM',
                                time_param_n = 18,
                                next_step_n = 3,
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V11', 'BUNKER1V15', 'BUNKER1V1', 'BUNKER1V16', 'BUNKER1V17', 'CIPV3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V2', 'BUNKER1V5', 'BUNKER1V14', 'BUNKER1V13'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'F_BRINE_OUT1V3'
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Промывка трубы 4875',
                                time_param_n = 19,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V11', 'BUNKER1V15', 'BUNKER1V1', 'BUNKER1V16', 'BUNKER1V17', 'CIPV3', 'BUNKER1V5', 'BUNKER1V14'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V2'
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Смена среды ',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'CIPV3', 'BUNKER1V11', 'BUNKER1V13', 'BUNKER1V15', 'BUNKER1V1', 'BUNKER1V16', 'BUNKER1V17', 'BUNKER1V14'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V2', 'BUNKER1V5'
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 20,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V11', 'BUNKER1V13', 'BUNKER1V15', 'BUNKER1V1', 'BUNKER1V16', 'BUNKER1V17', 'CIPV3'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V2', 'BUNKER1V5', 'BUNKER1V14'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'MCA5LINE4DO9'
                                            },
                                        },
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 22,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V13', 'BUNKER1V15', 'BUNKER1V1', 'BUNKER1V2', 'BUNKER1V16', 'BUNKER1V5', 'BUNKER1V14', 'BUNKER1V6', 'BUNKER1V21', 'BUNKER1V22', 'BUNKER1V23', 'BUNKER1V24', 'BUNKER1V25', 'BUNKER1V26', 'BUNKER1V27'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V11', 'BUNKER1V17', 'CIPV3'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Циркуляция',
                base_operation = 'WORK',
                props =
                    {
                    WORK_FILL_AND_OUT = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'P4875V43', 'P4850V43', 'P4870V43', 'P4840V43'
                            },
                        closed_devices = --Выключать
                            {
                            'BUNKER1V11', 'BUNKER1V13', 'BUNKER1V15', 'BUNKER1V5', 'BUNKER1V16', 'BUNKER1V21', 'BUNKER1V22', 'BUNKER1V23', 'BUNKER1V24', 'BUNKER1V25', 'BUNKER1V26', 'BUNKER1V27', 'BUNKER1V14', 'F_BRINE_IN1V41'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Пополнение',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V40'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE5DO12'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Циркуляция',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BUNKER1V1', 'BUNKER1V5', 'BUNKER1V6'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BUNKER1V2'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        devices = --Устройства
                                            {
                                            'BUNKER1M1'
                                            },
                                        pump_freq = 'POWER_PUMP_WORK',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = 'BUNKER1LS2',
            hatch = '',
            hatch2 = '',
            LS_down = 'BUNKER1LS1',
            LT = 'BUNKER1LT1',
            TE = '',
            lamp = '',
            },
        },
    [ 27 ] =
        {
        n          = 5,
        tech_type  = 21,
        name       = 'Линия воды WLINE',
        name_eplan = 'WLINE',
        name_BC    = 'WLINE5LineObj1',
        cooper_param_number = -1,
        base_tech_object = 'line',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_REQUEST = 'WLINE5DI1',
                    CIP_WASH_END = 'WLINE5DI2',
                    IGNORE_WATER_FLAG = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4850V41', 'P4870V41', 'P4875V41', 'P4840V41', 'P4790V41', 'BUNKER1V40', 'F_BRINE_IN1V41'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI1'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'WLINE5DO1'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'P4850V43', 'P4870V43', 'P4875V43', 'P4840V43', 'P4790V43', 'BUNKER1V43'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4875V42', 'P4850V42', 'P4870V42', 'P4840V42', 'P4790V42', 'F_BRINE_IN1V42'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 6,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'P4875V42', 'P4875V43', 'P4850V42', 'P4850V43', 'P4870V42', 'P4870V43', 'P4840V42', 'P4840V43', 'F_BRINE_IN1V42', 'P4790V42', 'BUNKER1V43'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'P4790V43'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = '',
            },
        },
    [ 28 ] =
        {
        n          = 3,
        tech_type  = 22,
        name       = 'Линия рассола BRN',
        name_eplan = 'BRN',
        name_BC    = 'BRN3LineObj1',
        cooper_param_number = -1,
        base_tech_object = 'line',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_REQUEST = 'BRN3DI1',
                    IGNORE_WATER_FLAG = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V14', 'BRINE_TANK1V15'
                            },
                        closed_devices = --Выключать
                            {
                            'BRINE_TANK1V21', 'BRINE_TANK1V22'
                            },
                        opened_upper_seat_v = --Верхние седла
                            {
                             --Группа
                                {
                                'BRINE_TANK1V21'
                                },
                             --Группа
                                {
                                'BRINE_TANK1V22'
                                },
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'BRN3DO1'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = '',
            },
        },
    [ 29 ] =
        {
        n          = 1,
        tech_type  = 21,
        name       = 'Танк (дозирование рассола)',
        name_eplan = 'F_BRINE_TANK',
        name_BC    = 'FBrineTankObj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '33 35',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Номер партии в танке',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'PART_NUMB1'
                },
            [ 8 ] =
                {
                name = 'Дата (день) производства партии в танке',
                value = 0,
                meter = 'д',
                oper = { -1 },
                nameLua = 'PART_DAY1'
                },
            [ 9 ] =
                {
                name = 'Дата (месяц) производства партии в танке',
                value = 0,
                meter = 'мес',
                oper = { -1 },
                nameLua = 'PART_MONTH1'
                },
            [ 10 ] =
                {
                name = 'Дата (год) производства партии в танке',
                value = 0,
                meter = 'г',
                oper = { -1 },
                nameLua = 'PART_YEAR1'
                },
            [ 11 ] =
                {
                name = 'Текущий набранный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_CURRENT'
                },
            [ 12 ] =
                {
                name = 'Заданный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_SET'
                },
            [ 13 ] =
                {
                name = 'Температура охлаждения',
                value = 4,
                meter = 'С',
                oper = { 2,4,5 },
                nameLua = 'BRINE_COOL_TEMP'
                },
            [ 14 ] =
                {
                name = 'Дельта температуры охлаждения',
                value = 0.5,
                meter = 'C',
                oper = { 2,4,5 },
                nameLua = 'DELTA_BRINE_COOL_TEMP'
                },
            [ 15 ] =
                {
                name = 'Время растворения',
                value = 15,
                meter = 'мин',
                oper = { 3 },
                nameLua = 'DISSOLUTION_TIME'
                },
            [ 16 ] =
                {
                name = 'Максимальный уровень для включения мойки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_MAX_LT'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "В танк"',
                value = 150,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_TANK_TIME'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Флипование"',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_FLUSH_TIME'
                },
            [ 19 ] =
                {
                name = 'Время дренажа после пропадания НУ',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 20 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 180,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 21 ] =
                {
                name = 'Производительность насоса',
                value = 95,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_PUMP_PERFORMANCE'
                },
            [ 22 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 23 ] =
                {
                name = 'Минимальный уровень для работы мешалки',
                value = 10,
                meter = '%',
                oper = { -1 },
                nameLua = 'MIX_MIN_LT'
                },
            [ 24 ] =
                {
                name = 'Дельта мин. уровня для включения мешалки',
                value = 1,
                meter = '%',
                oper = { -1 },
                nameLua = 'MIX_DELTA_LT'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 26 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 27 ] =
                {
                name = 'Время работы мешалки',
                value = 0,
                meter = 'мин',
                oper = { -1 },
                nameLua = 'MIX_TIME_ON'
                },
            [ 28 ] =
                {
                name = 'Время простоя мешалки',
                value = 0,
                meter = 'мин',
                oper = { -1 },
                nameLua = 'MIX_TIME_OFF'
                },
            [ 29 ] =
                {
                name = 'Время работы мешалки при наполнении',
                value = 5,
                meter = 'мин',
                oper = { 2 },
                nameLua = 'FILL_MIX_TIME_ON'
                },
            [ 30 ] =
                {
                name = 'Время простоя мешалки при наполнении',
                value = 1,
                meter = 'мин',
                oper = { 2 },
                nameLua = 'FILL_MIX_TIME_OFF'
                },
            [ 31 ] =
                {
                name = 'Время работы мешалки при хранении',
                value = 15,
                meter = 'мин',
                oper = { 4 },
                nameLua = 'STORE_MIX_ON_PHASE1_TIME'
                },
            [ 32 ] =
                {
                name = 'Время простоя мешалки при хранении',
                value = 5,
                meter = 'мин',
                oper = { 4 },
                nameLua = 'STORE_MIX_WAIT_PHASE1_TIME'
                },
            [ 33 ] =
                {
                name = 'Время работы мешалки при выдаче',
                value = 30,
                meter = 'мин',
                oper = { 5 },
                nameLua = 'OUT_MIX_ON_PHASE1_TIME'
                },
            [ 34 ] =
                {
                name = 'Время простоя мешалки при выдаче',
                value = 1,
                meter = 'мин',
                oper = { 5 },
                nameLua = 'OUT_MIX_WAIT_PHASE1_TIME'
                },
            [ 35 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 36 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 37 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 38 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 39 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 40 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 41 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 42 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 43 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 44 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 45 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 46 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 47 ] =
                {
                name = 'Задержка выключения выдачи по НУ',
                value = 5,
                meter = 'с',
                oper = { 4 },
                nameLua = 'DELAY_OUT_OFF_TIME'
                },
            [ 48 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 49 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 50 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE2DI1',
                    MEDIUM_CHANGE_REQUEST = 'Нет',
                    CIP_WASH_END = 'MCA5LINE2DI3',
                    CIP_WASH_REQUEST = 'Нет',
                    NEED_COOLING = 'false',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'Нет',
                    MIX_NODE_MIX_OFF_TIME = 'Нет',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'MCA5LINE2DO1', 'F_BRINE_TANK1V11', 'F_BRINE_TANK1V13', 'F_BRINE_TANK1V1', 'F_BRINE_TANK1V15', 'F_BRINE_TANK1V17'
                            },
                        closed_devices = --Выключать
                            {
                            'F_BRINE_OUT1V13', 'F_BRINE_OUT1V11', 'F_BRINE_TANK2V17', 'F_BRINE_OUT1V17', 'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_IN1V1', 'F_BRINE_TANK1V21', 'CIPV3'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE2DI1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка танка',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK1V12', 'F_BRINE_TANK1V16'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'MCA5LINE2DI2'
                                            },
                                        devices = --Устройства
                                            {
                                            'CIPM1'
                                            },
                                        pump_freq = 21,
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Флипование',
                                time_param_n = 18,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK1V12', 'F_BRINE_TANK1V16'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'F_BRINE_OUT1V1'
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 19,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_TANK1V12', 'F_BRINE_TANK1V16'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    OPERATION_AFTER_FILL = '3',
                    NEED_COOLING = 'true',
                    COOLING_TEMPERATURE = 'BRINE_COOL_TEMP',
                    COOLING_TEMPERATURE_DELTA = 'DELTA_BRINE_COOL_TEMP',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'FILL_MIX_TIME_ON',
                    MIX_NODE_MIX_OFF_TIME = 'FILL_MIX_TIME_OFF',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK1V12', 'F_BRINE_TANK1V11', 'F_BRINE_TANK1V13', 'F_BRINE_TANK1V1', 'F_BRINE_TANK1V15', 'F_BRINE_TANK1V17', 'F_BRINE_TANK1V16', 'F_BRINE_OUT1V1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Растворение',
                base_operation = 'LEAVENING',
                props =
                    {
                    LEAVENING_TIME = 'DISSOLUTION_TIME',
                    OPERATION_AFTER = '4',
                    NEED_COOLING = 'false',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'Нет',
                    MIX_NODE_MIX_OFF_TIME = 'Нет',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK1V12', 'F_BRINE_TANK1V11', 'F_BRINE_TANK1V13', 'F_BRINE_TANK1V1', 'F_BRINE_TANK1V15', 'F_BRINE_TANK1V17', 'F_BRINE_TANK1V16', 'F_BRINE_OUT1V1', 'F_BRINE_IN1V1'
                            },
                        },
                    },
                },
            [ 4 ] =
                {
                name = 'Хранение',
                base_operation = 'STORING',
                props =
                    {
                    NEED_COOLING = 'true',
                    COOLING_TEMPERATURE = 'BRINE_COOL_TEMP',
                    COOLING_TEMPERATURE_DELTA = 'DELTA_BRINE_COOL_TEMP',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'STORE_MIX_ON_PHASE1_TIME',
                    MIX_NODE_MIX_OFF_TIME = 'STORE_MIX_WAIT_PHASE1_TIME',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK1V12', 'F_BRINE_TANK1V11', 'F_BRINE_TANK1V13', 'F_BRINE_TANK1V1', 'F_BRINE_TANK1V15', 'F_BRINE_TANK1V17', 'F_BRINE_TANK1V16', 'F_BRINE_OUT1V1', 'F_BRINE_IN1V1'
                            },
                        },
                    },
                },
            [ 5 ] =
                {
                name = 'Выдача',
                base_operation = 'OUT',
                props =
                    {
                    NEED_STORING_AFTER = 'true',
                    NEED_COOLING = 'true',
                    COOLING_TEMPERATURE = 'BRINE_COOL_TEMP',
                    COOLING_TEMPERATURE_DELTA = 'DELTA_BRINE_COOL_TEMP',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'OUT_MIX_ON_PHASE1_TIME',
                    MIX_NODE_MIX_OFF_TIME = 'OUT_MIX_WAIT_PHASE1_TIME',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'F_BRINE_TANK1V1'
                            },
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK1V12', 'F_BRINE_TANK1V11', 'F_BRINE_TANK1V13', 'F_BRINE_TANK1V15', 'F_BRINE_TANK1V17', 'F_BRINE_TANK1V16', 'F_BRINE_IN1V1'
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = 'F_BRINE_TANK1LS2',
            hatch = 'F_BRINE_TANK1GS1',
            hatch2 = '',
            LS_down = 'F_BRINE_TANK1LS1',
            LT = 'F_BRINE_TANK1LT1',
            TE = 'F_BRINE_TANK1TE1',
            lamp = '',
            },
        },
    [ 30 ] =
        {
        n          = 2,
        tech_type  = 21,
        name       = 'Танк (дозирование рассола)',
        name_eplan = 'F_BRINE_TANK',
        name_BC    = 'FBrineTankObj2',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        attached_objects = '34 36',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 1,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 7 ] =
                {
                name = 'Номер партии в танке',
                value = 0,
                meter = '№',
                oper = { -1 },
                nameLua = 'PART_NUMB1'
                },
            [ 8 ] =
                {
                name = 'Дата (день) производства партии в танке',
                value = 0,
                meter = 'д',
                oper = { -1 },
                nameLua = 'PART_DAY1'
                },
            [ 9 ] =
                {
                name = 'Дата (месяц) производства партии в танке',
                value = 0,
                meter = 'мес',
                oper = { -1 },
                nameLua = 'PART_MONTH1'
                },
            [ 10 ] =
                {
                name = 'Дата (год) производства партии в танке',
                value = 0,
                meter = 'г',
                oper = { -1 },
                nameLua = 'PART_YEAR1'
                },
            [ 11 ] =
                {
                name = 'Текущий набранный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_CURRENT'
                },
            [ 12 ] =
                {
                name = 'Заданный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_SET'
                },
            [ 13 ] =
                {
                name = 'Температура охлаждения',
                value = 4,
                meter = 'С',
                oper = { 2,4,5 },
                nameLua = 'BRINE_COOL_TEMP'
                },
            [ 14 ] =
                {
                name = 'Дельта температуры охлаждения',
                value = 0.5,
                meter = 'C',
                oper = { 2,4,5 },
                nameLua = 'DELTA_BRINE_COOL_TEMP'
                },
            [ 15 ] =
                {
                name = 'Время растворения',
                value = 15,
                meter = 'мин',
                oper = { 3 },
                nameLua = 'DISSOLUTION_TIME'
                },
            [ 16 ] =
                {
                name = 'Максимальный уровень для включения мойки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_MAX_LT'
                },
            [ 17 ] =
                {
                name = 'Время шага мойки "В танк"',
                value = 150,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_TANK_TIME'
                },
            [ 18 ] =
                {
                name = 'Время шага мойки "Флипование"',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_IN_FLUSH_TIME'
                },
            [ 19 ] =
                {
                name = 'Время дренажа после пропадания НУ',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 20 ] =
                {
                name = 'Максимальное время дренажа после мойки',
                value = 180,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 21 ] =
                {
                name = 'Производительность насоса',
                value = 95,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_PUMP_PERFORMANCE'
                },
            [ 22 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 23 ] =
                {
                name = 'Минимальный уровень для работы мешалки',
                value = 10,
                meter = '%',
                oper = { -1 },
                nameLua = 'MIX_MIN_LT'
                },
            [ 24 ] =
                {
                name = 'Дельта мин. уровня для включения мешалки',
                value = 1,
                meter = '%',
                oper = { -1 },
                nameLua = 'MIX_DELTA_LT'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 26 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 27 ] =
                {
                name = 'Время работы мешалки',
                value = 0,
                meter = 'мин',
                oper = { -1 },
                nameLua = 'MIX_TIME_ON'
                },
            [ 28 ] =
                {
                name = 'Время простоя мешалки',
                value = 0,
                meter = 'мин',
                oper = { -1 },
                nameLua = 'MIX_TIME_OFF'
                },
            [ 29 ] =
                {
                name = 'Время работы мешалки при наполнении',
                value = 5,
                meter = 'мин',
                oper = { 2 },
                nameLua = 'FILL_MIX_TIME_ON'
                },
            [ 30 ] =
                {
                name = 'Время простоя мешалки при наполнении',
                value = 1,
                meter = 'мин',
                oper = { 2 },
                nameLua = 'FILL_MIX_TIME_OFF'
                },
            [ 31 ] =
                {
                name = 'Время работы мешалки при хранении',
                value = 15,
                meter = 'мин',
                oper = { 4 },
                nameLua = 'STORE_MIX_ON_PHASE1_TIME'
                },
            [ 32 ] =
                {
                name = 'Время простоя мешалки при хранении',
                value = 5,
                meter = 'мин',
                oper = { 4 },
                nameLua = 'STORE_MIX_WAIT_PHASE1_TIME'
                },
            [ 33 ] =
                {
                name = 'Время работы мешалки при выдаче',
                value = 30,
                meter = 'мин',
                oper = { 5 },
                nameLua = 'OUT_MIX_ON_PHASE1_TIME'
                },
            [ 34 ] =
                {
                name = 'Время простоя мешалки при выдаче',
                value = 1,
                meter = 'мин',
                oper = { 5 },
                nameLua = 'OUT_MIX_WAIT_PHASE1_TIME'
                },
            [ 35 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 36 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 37 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 38 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 39 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 40 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 41 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 42 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 43 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 44 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 45 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 46 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 47 ] =
                {
                name = 'Задержка выключения выдачи по НУ',
                value = 5,
                meter = 'с',
                oper = { 5 },
                nameLua = 'DELAY_OUT_OFF_TIME'
                },
            [ 48 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 49 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 50 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'true',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    DI_CIP_FREE = 'MCA5LINE2DI1',
                    MEDIUM_CHANGE_REQUEST = 'Нет',
                    CIP_WASH_END = 'MCA5LINE2DI3',
                    CIP_WASH_REQUEST = 'Нет',
                    NEED_COOLING = 'false',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'Нет',
                    MIX_NODE_MIX_OFF_TIME = 'Нет',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_TANK2V1', 'F_BRINE_TANK2V15', 'F_BRINE_TANK2V17', 'MCA5LINE2DO2'
                            },
                        closed_devices = --Выключать
                            {
                            'F_BRINE_OUT1V13', 'F_BRINE_OUT1V11', 'F_BRINE_OUT1V17', 'F_BRINE_TANK2V21', 'F_BRINE_TANK1V17', 'F_BRINE_TANK1V13', 'F_BRINE_TANK1V11', 'F_BRINE_IN1V2', 'CIPV3'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE2DI1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка танка',
                                time_param_n = 17,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK2V12', 'F_BRINE_TANK2V16'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'MCA5LINE2DI2'
                                            },
                                        devices = --Устройства
                                            {
                                            'CIPM1'
                                            },
                                        pump_freq = 21,
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Флипование',
                                time_param_n = 18,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK2V12', 'F_BRINE_TANK2V16'
                                    },
                                opened_upper_seat_v = --Верхние седла
                                    {
                                     --Группа
                                        {
                                        'F_BRINE_OUT1V2'
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 19,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_TANK2V12', 'F_BRINE_TANK2V16'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    OPERATION_AFTER_FILL = '3',
                    NEED_COOLING = 'true',
                    COOLING_TEMPERATURE = 'BRINE_COOL_TEMP',
                    COOLING_TEMPERATURE_DELTA = 'DELTA_BRINE_COOL_TEMP',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'FILL_MIX_TIME_ON',
                    MIX_NODE_MIX_OFF_TIME = 'FILL_MIX_TIME_OFF',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK2V12', 'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_TANK2V1', 'F_BRINE_TANK2V15', 'F_BRINE_TANK2V17', 'F_BRINE_TANK2V16', 'F_BRINE_OUT1V2'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Растворение',
                base_operation = 'LEAVENING',
                props =
                    {
                    LEAVENING_TIME = 'DISSOLUTION_TIME',
                    OPERATION_AFTER = '4',
                    NEED_COOLING = 'false',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'Нет',
                    MIX_NODE_MIX_OFF_TIME = 'Нет',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK2V12', 'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_TANK2V1', 'F_BRINE_TANK2V15', 'F_BRINE_TANK2V17', 'F_BRINE_TANK2V16', 'F_BRINE_OUT1V2', 'F_BRINE_IN1V2'
                            },
                        },
                    },
                },
            [ 4 ] =
                {
                name = 'Хранение',
                base_operation = 'STORING',
                props =
                    {
                    NEED_COOLING = 'true',
                    COOLING_TEMPERATURE = 'BRINE_COOL_TEMP',
                    COOLING_TEMPERATURE_DELTA = 'DELTA_BRINE_COOL_TEMP',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'STORE_MIX_ON_PHASE1_TIME',
                    MIX_NODE_MIX_OFF_TIME = 'STORE_MIX_WAIT_PHASE1_TIME',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK2V12', 'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_TANK2V1', 'F_BRINE_TANK2V15', 'F_BRINE_TANK2V17', 'F_BRINE_TANK2V16', 'F_BRINE_IN1V2', 'F_BRINE_OUT1V2'
                            },
                        },
                    },
                },
            [ 5 ] =
                {
                name = 'Выдача',
                base_operation = 'OUT',
                props =
                    {
                    NEED_STORING_AFTER = 'true',
                    NEED_COOLING = 'true',
                    COOLING_TEMPERATURE = 'BRINE_COOL_TEMP',
                    COOLING_TEMPERATURE_DELTA = 'DELTA_BRINE_COOL_TEMP',
                    NEED_PAUSE_COOLING = 'true',
                    NEED_MIXING = 'true',
                    MIX_NODE_MIX_OPERATION = '1',
                    MIX_NODE_MIX_SPEED = 'Нет',
                    MIX_NODE_MIX_ON_TIME = 'OUT_MIX_ON_PHASE1_TIME',
                    MIX_NODE_MIX_OFF_TIME = 'OUT_MIX_WAIT_PHASE1_TIME',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'F_BRINE_TANK2V1'
                            },
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK2V12', 'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_TANK2V15', 'F_BRINE_TANK2V17', 'F_BRINE_TANK2V16', 'F_BRINE_IN1V2'
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = 'F_BRINE_TANK2LS2',
            hatch = 'F_BRINE_TANK2GS1',
            hatch2 = '',
            LS_down = 'F_BRINE_TANK2LS1',
            LT = 'F_BRINE_TANK2LT1',
            TE = 'F_BRINE_TANK2TE1',
            lamp = '',
            },
        },
    [ 31 ] =
        {
        n          = 1,
        tech_type  = 22,
        name       = 'Линия наполнения водой (Танки дозирования рассола)',
        name_eplan = 'F_BRINE_IN',
        name_BC    = 'FBrineLineInObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_in',
        tank_groups =
            {
                tanks = '29 30',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 1 },
                nameLua = 'OPER_MODE'
                },
            [ 10 ] =
                {
                name = 'Текущий приемник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 1 },
                nameLua = 'OPER_DESTINATION'
                },
            [ 11 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 1 },
                nameLua = 'WATER_FLAG'
                },
            [ 12 ] =
                {
                name = 'Принятый объем продукта',
                value = 0,
                meter = 'л',
                oper = { 1 },
                nameLua = 'PROD_V'
                },
            [ 13 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 18 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    CONCENTRATION = 'Нет',
                    DELTA_CONCENTRATION = 'Нет',
                    IS_END_ON_FULL_TANK = 'true',
                    MOVE_TO_STEP_WAITING_BY_SIGNALS = 'false',
                    NEED_PAUSE_AFTER_FULL_LAST_TANK = 'false',
                    CONTINUE_PRODUCT_PUSH = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'P4875V43', 'P4850V43', 'P4870V43', 'P4840V43'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE5DI11'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'WLINE5DO12'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'В танк 1',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_TANK',
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_IN1V1'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'В танк 2',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_IN1V2'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = 'F_BRINE_IN1FQT1',
            },
        },
    [ 32 ] =
        {
        n          = 1,
        tech_type  = 23,
        name       = 'Линия выдачи (Танки дозирования рассола)',
        name_eplan = 'F_BRINE_OUT',
        name_BC    = 'FBrineLineOutObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_out',
        tank_groups =
            {
                tanks = '29 30',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Текущий источник (№-номер танка, -1-вода)',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_SRC'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Режим работы операции, 0-авто, 1-ручной',
                value = 1,
                meter = 'шт',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 6 ] =
                {
                name = 'Максимальное время операции «Мойка» ',
                value = 120,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'WASH_TIME_MAX'
                },
            [ 7 ] =
                {
                name = 'Время шага «Мойка линии» операции «Мойка»',
                value = 120,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_STEP1_TIME'
                },
            [ 8 ] =
                {
                name = 'Время шага «Флипование» операции «Мойка»',
                value = 22,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_STEP2_TIME'
                },
            [ 9 ] =
                {
                name = 'Время шага «Дренаж» операции «Мойка»',
                value = 50,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 10 ] =
                {
                name = 'Производительность насоса',
                value = 80,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_PUMP_PERFORMANCE'
                },
            [ 11 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 12 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 13 ] =
                {
                name = 'Производительность насоса',
                value = 80,
                meter = '%',
                oper = { 2 },
                nameLua = 'PUMP_PERFORMANCE'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка линии',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_REQUEST = 'Нет',
                    CIP_WASH_END = 'MCA5LINE4DI3',
                    IGNORE_WATER_FLAG = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'F_BRINE_OUT1V11', 'F_BRINE_OUT1V13', 'F_BRINE_OUT1V15', 'F_BRINE_OUT1V17', 'MCA5LINE4DO6'
                            },
                        closed_devices = --Выключать
                            {
                            'F_BRINE_TANK1V13', 'F_BRINE_TANK1V11', 'F_BRINE_TANK2V11', 'F_BRINE_TANK2V13', 'F_BRINE_TANK1V17', 'F_BRINE_TANK2V17', 'F_BRINE_OUT1V3', 'F_BRINE_OUT1V1', 'F_BRINE_OUT1V2'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE4DI1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 7,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_OUT1V12', 'F_BRINE_OUT1V16'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'MCA5LINE4DI2'
                                            },
                                        devices = --Устройства
                                            {
                                            'F_BRINE_OUT1M2'
                                            },
                                        pump_freq = 10,
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Флипование',
                                time_param_n = 8,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_OUT1V12', 'F_BRINE_OUT1V16'
                                    },
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'F_BRINE_OUT1V1', 'F_BRINE_OUT1V2'
                                        },
                                     --Группа
                                        {
                                        'F_BRINE_OUT1V3'
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 9,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_OUT1V15', 'F_BRINE_OUT1V17', 'F_BRINE_OUT1V13'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_OUT1V12', 'F_BRINE_OUT1V16'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Выдача',
                base_operation = 'OUT',
                props =
                    {
                    product_request = 'PFM1DI4',
                    water_request = 'Нет',
                    USE_VOLUME = 'false',
                    CONTINUE_WATER_PUSH = 'false',
                    NEED_PAUSE_AFTER_EMPTY_LAST_TANK = 'true',
                    WAITING_WATER_REQUEST = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'F_BRINE_OUT1V4', 'F_BRINE_OUT1V3'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                devices = --Устройства
                                    {
                                    'F_BRINE_OUT1M2'
                                    },
                                pump_freq = 13,
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_KEY',
                                },
                            [ 2 ] =
                                {
                                name = 'Из танка 1',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'OUT_TANK',
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_OUT1V1'
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Из танка 2',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_OUT1V2'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = '',
            },
        },
    [ 33 ] =
        {
        n          = 1,
        tech_type  = 25,
        name       = 'Узел охлаждения дозирование рассола Танк',
        name_eplan = 'F_BRINE_TANK',
        name_BC    = 'FBrineTankCoolObj1',
        cooper_param_number = -1,
        base_tech_object = 'cooler_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура охлаждения',
                value = 4,
                meter = 'C',
                oper = { 1 },
                nameLua = 'COOL_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температура охлаждения',
                value = 0.5,
                meter = 'C',
                oper = { 1 },
                nameLua = 'TE_COOL_DELTA'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Охлаждение',
                base_operation = 'COOLING',
                props =
                    {
                    COOL_TEMPERATURE = 'COOL_TEMPERATURE',
                    COOL_DELTA_TEMPERATURE = 'TE_COOL_DELTA',
                    FINISH_COLD_WATER_PUSHING_TEMPERATURE = 'Нет',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK1V21'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING',
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_TANK1V21'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'F_BRINE_TANK1TE1',
            TE2 = '',
            },
        },
    [ 34 ] =
        {
        n          = 2,
        tech_type  = 25,
        name       = 'Узел охлаждения дозирование рассола Танк',
        name_eplan = 'F_BRINE_TANK',
        name_BC    = 'FBrineTankCoolObj2',
        cooper_param_number = -1,
        base_tech_object = 'cooler_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура охлаждения',
                value = 4,
                meter = 'C',
                oper = { 1 },
                nameLua = 'COOL_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температура охлаждения',
                value = 0.5,
                meter = 'C',
                oper = { 1 },
                nameLua = 'TE_COOL_DELTA'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Охлаждение',
                base_operation = 'COOLING',
                props =
                    {
                    COOL_TEMPERATURE = 'COOL_TEMPERATURE',
                    COOL_DELTA_TEMPERATURE = 'TE_COOL_DELTA',
                    FINISH_COLD_WATER_PUSHING_TEMPERATURE = 'Нет',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK2V21'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING',
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_TANK2V21'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'F_BRINE_TANK2TE1',
            TE2 = '',
            },
        },
    [ 35 ] =
        {
        n          = 1,
        tech_type  = 24,
        name       = 'Узел перемешивания дозирование рассола Танк',
        name_eplan = 'F_BRINE_TANK',
        name_BC    = 'FBrineTankMixObj1',
        cooper_param_number = -1,
        base_tech_object = 'mix_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время работы мешалки при перемешивании',
                value = 1,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'MIX_TIME_ON'
                },
            [ 4 ] =
                {
                name = 'Время простоя мешалки при перемешивании',
                value = 10,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'MIX_TIME_OFF'
                },
            [ 5 ] =
                {
                name = 'Время перемешивания',
                value = 600,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'TOTAL_MIX_TIME'
                },
            [ 6 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 7 ] =
                {
                name = 'Минимальный уровень для работы мешалки',
                value = 10,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_MIN_LT'
                },
            [ 8 ] =
                {
                name = 'Дельта мин. уровня для включения мешалки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_DELTA_LT'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Перемешивание',
                base_operation = 'MIXING',
                props =
                    {
                    WORK_WITH_SECTIONS = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа мешалки',
                                time_param_n = 3,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK1M1'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Простой мешалки',
                                time_param_n = 4,
                                next_step_n = 1,
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_TANK1M1'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            hatch = 'F_BRINE_TANK1GS1',
            bar = '',
            LT = 'F_BRINE_TANK1LT1',
            mix = 'F_BRINE_TANK1M1',
            },
        },
    [ 36 ] =
        {
        n          = 2,
        tech_type  = 24,
        name       = 'Узел перемешивания дозирование рассола Танк',
        name_eplan = 'F_BRINE_TANK',
        name_BC    = 'FBrineTankMixObj2',
        cooper_param_number = -1,
        base_tech_object = 'mix_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время работы мешалки при перемешивании',
                value = 1,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'MIX_TIME_ON'
                },
            [ 4 ] =
                {
                name = 'Время простоя мешалки при перемешивании',
                value = 10,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'MIX_TIME_OFF'
                },
            [ 5 ] =
                {
                name = 'Время перемешивания',
                value = 600,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'TOTAL_MIX_TIME'
                },
            [ 6 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 7 ] =
                {
                name = 'Минимальный уровень для работы мешалки',
                value = 10,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_MIN_LT'
                },
            [ 8 ] =
                {
                name = 'Дельта мин. уровня для включения мешалки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'MIX_DELTA_LT'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Перемешивание',
                base_operation = 'MIXING',
                props =
                    {
                    WORK_WITH_SECTIONS = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа мешалки',
                                time_param_n = 3,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'F_BRINE_TANK2M1'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Простой мешалки',
                                time_param_n = 4,
                                next_step_n = 1,
                                closed_devices = --Выключать
                                    {
                                    'F_BRINE_TANK2M1'
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            hatch = 'F_BRINE_TANK2GS1',
            bar = '',
            LT = 'F_BRINE_TANK2LT1',
            mix = 'F_BRINE_TANK2M1',
            },
        },
    [ 37 ] =
        {
        n          = 1,
        tech_type  = 26,
        name       = 'Мойка',
        name_eplan = '',
        name_BC    = 'WashObj1',
        cooper_param_number = -1,
        base_tech_object = 'CIP_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка Сыроизготовитель №1 + Линия Сыворотки W2',
                base_operation = 'WASHING_CIP',
                },
            },
        },
    [ 38 ] =
        {
        n          = 2,
        tech_type  = 27,
        name       = 'Мойка',
        name_eplan = '',
        name_BC    = 'WashObj2',
        cooper_param_number = -1,
        base_tech_object = 'CIP_node',
        tank_groups =
            {
                CIP_objects = '19 22',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка Солильная ванна BV 29-2.2 4885 + Танк рассола №1',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_REQUEST = 'ALPMAGW5DI488501',
                    },
                },
            },
        },
    [ 39 ] =
        {
        n          = 2,
        tech_type  = 28,
        name       = 'Линия выдачи сыворотки W (Резерв)',
        name_eplan = 'W',
        name_BC    = 'W2LineOutObj1',
        cooper_param_number = -1,
        base_tech_object = 'user_object',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время шага "Завершение мойки"',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_END'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 6 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 7 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'WATER_FLAG'
                },
            [ 8 ] =
                {
                name = 'Текущий источник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_SRC'
                },
            [ 9 ] =
                {
                name = 'Выданный объем продукта',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 10 ] =
                {
                name = 'Объем линии',
                value = 500,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_LINE'
                },
            [ 11 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 12 ] =
                {
                name = 'Требуемый объем выдачи',
                value = 0,
                meter = 'л',
                oper = { -1 },
                nameLua = 'V_LINE_OUT'
                },
            [ 13 ] =
                {
                name = 'Дополнительный объем проталкивания в дренаж',
                value = 0,
                meter = 'л',
                oper = { -1 },
                nameLua = 'WATER_V_ADD'
                },
            [ 14 ] =
                {
                name = 'Давление продукта',
                value = 2,
                meter = 'бар',
                oper = { 2 },
                nameLua = 'PRESSURE_VALUE'
                },
            [ 15 ] =
                {
                name = 'Минимальное давление для отсутствия потока',
                value = 0.3,
                meter = 'бар',
                oper = { 1 },
                nameLua = 'PRESSURE_VALUE_MIN'
                },
            [ 16 ] =
                {
                name = 'Дельта минимального давления',
                value = 0.2,
                meter = 'бар',
                oper = { 1 },
                nameLua = 'PRESSURE_VALUE_DELTA'
                },
            [ 17 ] =
                {
                name = 'Время отсутствия давления',
                value = 10,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_PRESSURE_VALUE_MIN'
                },
            [ 18 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 19 ] =
                {
                name = 'Производительность насоса во время мойки',
                value = 85,
                meter = '%',
                oper = { 1 },
                nameLua = 'POWER_PUMP_CIP'
                },
            [ 20 ] =
                {
                name = 'Производительность насоса во время выдачи',
                value = 90,
                meter = '%',
                oper = { -1 },
                nameLua = 'POWER_PUMP_WORK'
                },
            [ 21 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 22 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        required_FB = --Сигналы для включения
                            {
                            'MCA5LINE1DI1'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DI = --DI
                                    {
                                    'MCA5LINE1DI2'
                                    },
                                pump_freq = 'POWER_PUMP_CIP',
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'W2DO1'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Завершение мойки',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'W2DO2'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Выдача',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        required_FB = --Сигналы для включения
                            {
                            'W2DI11'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'W2DO11'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'Проталкивание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Из Танка №1',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        },
    [ 40 ] =
        {
        n          = 2,
        tech_type  = 29,
        name       = 'Узел давления ПИД W (Резерв)',
        name_eplan = 'W',
        name_BC    = 'W2PressObj1',
        cooper_param_number = -1,
        base_tech_object = 'user_object',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Давление продукта',
                value = 2,
                meter = 'бар',
                oper = { 1 },
                nameLua = 'PRESSURE_VALUE'
                },
            [ 4 ] =
                {
                name = 'Минимальное давление для отсутствия потока',
                value = 0.3,
                meter = 'бар',
                oper = { 1 },
                nameLua = 'PRESSURE_VALUE_MIN'
                },
            [ 5 ] =
                {
                name = 'Дельта минимального давления',
                value = 0.2,
                meter = 'бар',
                oper = { 1 },
                nameLua = 'PRESSURE_VALUE_DELTA'
                },
            [ 6 ] =
                {
                name = 'Время отсутствия давления',
                value = 10,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_PRESSURE_VALUE_MIN'
                },
            [ 7 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Работа',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        },
    [ 41 ] =
        {
        n          = 7,
        tech_type  = 30,
        name       = 'Обрат Узел расхода O',
        name_eplan = 'O',
        name_BC    = 'O7FlowObj1',
        cooper_param_number = -1,
        base_tech_object = 'flow_node_PID',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Расход продукта',
                value = 10,
                meter = 'м3/ч',
                oper = { 1 },
                nameLua = 'FLOW_VALUE'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        system_parameters =
            {
            P_k =
                {
                value = 0.5,
                },
            P_Ti =
                {
                value = 10,
                },
            P_Td =
                {
                value = 0.2,
                },
            P_dt =
                {
                value = 1000,
                },
            P_max =
                {
                value = 200,
                },
            P_min =
                {
                value = 0,
                },
            P_acceleration_time =
                {
                value = 2,
                },
            P_is_manual_mode =
                {
                value = 0,
                },
            P_U_manual =
                {
                value = 65,
                },
            P_k2 =
                {
                value = 0,
                },
            P_Ti2 =
                {
                value = 0,
                },
            P_Td2 =
                {
                value = 0,
                },
            P_out_max =
                {
                value = 100,
                },
            P_out_min =
                {
                value = 0,
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Работа',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'LA_TANK1M3'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            M1 = 'LA_TANK1M3',
            FQT1 = 'LA_TANK1FQT1',
            },
        },
    [ 42 ] =
        {
        n          = 4,
        tech_type  = 31,
        name       = 'Линия наполнения BRN',
        name_eplan = 'BRN',
        name_BC    = 'BRN4LineInObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_in',
        tank_groups =
            {
                tanks = '29 30',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время мойки основной линии',
                value = 600,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH'
                },
            [ 4 ] =
                {
                name = 'Время промывки седел клапанов',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_SED'
                },
            [ 5 ] =
                {
                name = 'Время промывки дренажа',
                value = 2,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_DRAINAGE'
                },
            [ 6 ] =
                {
                name = 'Время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_DRAINAGE'
                },
            [ 7 ] =
                {
                name = 'Флаг использования бачка лимонной кислоты',
                value = 0,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'ACTIVITY_TANK'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 10 ] =
                {
                name = 'Текущий приемник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_DESTINATION'
                },
            [ 11 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'WATER_FLAG'
                },
            [ 12 ] =
                {
                name = 'Принятый объем продукта',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 13 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Электропроводность основы',
                value = 130,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'CONCENTRATION'
                },
            [ 16 ] =
                {
                name = 'Дельта электропроводности основы',
                value = 10,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'D_CONCENTRATION'
                },
            [ 17 ] =
                {
                name = 'Время отсутствия расхода для завершения наполнения',
                value = 60,
                meter = 'с',
                oper = { 2 },
                nameLua = 'NO_FLOW_TIME'
                },
            [ 18 ] =
                {
                name = 'Минимальный расход для завершения дренажа',
                value = 0.4,
                meter = 'м куб./ч',
                oper = { 2 },
                nameLua = 'MIN_FLOW'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_REQUEST = 'BRN4DI1',
                    CIP_WASH_END = 'BRN4DI3',
                    IGNORE_WATER_FLAG = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'BRN4V1', 'BRN4V2'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BRN4DI1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 3,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'BRN4V34', 'BRN4V35', 'BRN4V36'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN4DO1'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Промывка седел',
                                time_param_n = 4,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'BRN4V34', 'BRN4V35', 'BRN4V36'
                                    },
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'BRN4V1'
                                        },
                                     --Группа
                                        {
                                        'BRN4V2'
                                        },
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN4DO1'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Промывка дренажа',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRN4V34', 'BRN4V36'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRN4V35'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN4DO1'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 6,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'BRN4V34'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRN4V35', 'BRN4V36'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    CONCENTRATION = 'CONCENTRATION',
                    DELTA_CONCENTRATION = 'D_CONCENTRATION',
                    IS_END_ON_FULL_TANK = 'false',
                    MOVE_TO_STEP_WAITING_BY_SIGNALS = 'false',
                    NEED_PAUSE_AFTER_FULL_LAST_TANK = 'true',
                    CONTINUE_PRODUCT_PUSH = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'BRN4V36'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'BRN4DO11'
                                    },
                                },
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'BRN4DI11', 'BRN4DO12' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_KEY',
                                },
                            [ 2 ] =
                                {
                                name = 'В дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'BRN4V34'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRN4V35'
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'В танк №1',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_TANK',
                                opened_devices = --Включать
                                    {
                                    'BRN4V1', 'F_BRINE_TANK1V1'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRN4V34', 'BRN4V35'
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'В танк №2',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'BRN4V2', 'F_BRINE_TANK2V1'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'BRN4V34', 'BRN4V35'
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'В танк №3 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 6 ] =
                                {
                                name = 'В танк №4 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 7 ] =
                                {
                                name = 'В танк №5 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 8 ] =
                                {
                                name = 'Запрос проталкивания',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'PRODUCT_PUSH',
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BRN4DO13'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = 'BRN4QT1',
            product_CTR = '',
            },
        },
    [ 43 ] =
        {
        n          = 7,
        tech_type  = 32,
        name       = 'Линия наполнения BERTSCH O',
        name_eplan = 'BERTSCH_O',
        name_BC    = 'O7LineInObj2',
        cooper_param_number = -1,
        base_tech_object = 'line_in',
        attached_objects = '41',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время мойки основной линии',
                value = 600,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH'
                },
            [ 4 ] =
                {
                name = 'Время промывки седел клапанов',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_SED'
                },
            [ 5 ] =
                {
                name = 'Время промывки дренажа',
                value = 2,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_DRAINAGE'
                },
            [ 6 ] =
                {
                name = 'Время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_DRAINAGE'
                },
            [ 7 ] =
                {
                name = 'Флаг использования бачка лимонной кислоты',
                value = 0,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'ACTIVITY_TANK'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 10 ] =
                {
                name = 'Текущий приемник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_DESTINATION'
                },
            [ 11 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'WATER_FLAG'
                },
            [ 12 ] =
                {
                name = 'Принятый объем продукта',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 13 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Электропроводность основы',
                value = 3,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'CONCENTRATION'
                },
            [ 16 ] =
                {
                name = 'Дельта электропроводности основы',
                value = 0.2,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'D_CONCENTRATION'
                },
            [ 17 ] =
                {
                name = 'Время отсутствия расхода для завершения наполнения',
                value = 60,
                meter = 'с',
                oper = { 2 },
                nameLua = 'NO_FLOW_TIME'
                },
            [ 18 ] =
                {
                name = 'Минимальный расход для завершения дренажа',
                value = 0.4,
                meter = 'м куб./ч',
                oper = { 2 },
                nameLua = 'MIN_FLOW'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_END = 'O7DI2',
                    IGNORE_WATER_FLAG = 'false',
                    NEED_FLOW_CONTROL = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'LA_TANK1V101'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BERTSCH_MOZ_GW1DI1'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'UF1_O7DI2', 'O7DO2' }, 0, },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 3,
                                next_step_n = 2,
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI1', 'UF1_O7DO1' }, 0, },
                                    { { 'UF1_O7DI1', 'O7DO1' }, 0, },
                                    { { 'O7DI1', 'BERTSCH_MOZ_GW1DO1' }, 0, },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Промывка седел',
                                time_param_n = 4,
                                next_step_n = 3,
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'LA_TANK1V101'
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI1', 'UF1_O7DO1' }, 0, },
                                    { { 'UF1_O7DI1', 'O7DO1' }, 0, },
                                    { { 'O7DI1', 'BERTSCH_MOZ_GW1DO1' }, 0, },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Промывка дренажа',
                                time_param_n = 5,
                                next_step_n = 1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'O7DO2'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI1', 'UF1_O7DO1' }, 0, },
                                    { { 'UF1_O7DI1', 'O7DO1' }, 0, },
                                    { { 'O7DI1', 'BERTSCH_MOZ_GW1DO1' }, 0, },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 6,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'UF1_O7DO2'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    IS_END_ON_FULL_TANK = 'false',
                    MOVE_TO_STEP_WAITING_BY_SIGNALS = 'false',
                    NEED_PAUSE_AFTER_FULL_LAST_TANK = 'false',
                    CONTINUE_PRODUCT_PUSH = 'false',
                    NEED_FLOW_CONTROL = 'true',
                    NEED_PAUSE_FLOW_CONTROL = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        checked_devices = --Проверяемые устройства
                            {
                            'O7FQT1'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BERTSCH_MOZ_GW1DI11'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'UF1_O7DO11'
                                    },
                                },
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'BERTSCH_MOZ_GW1DI14', 'O7DO12' }, 0, },
                            { { 'O7DI12', 'BERTSCH_MOZ_GW1DO13' }, 0, },
                            { { 'O7DI13', 'BERTSCH_MOZ_GW1DO12' }, 0, },
                            { { 'O7DI14', 'BERTSCH_MOZ_GW1DO14' }, 0, },
                            },
                        AI_AO = --Группы AI -> AO AO ...
                            {
                             --Группа
                                {
                                'BERTSCH_MOZ_GW1AI11', 'O7AO11'
                                },
                             --Группа
                                {
                                'O7AI14', 'BERTSCH_MOZ_GW1AO11'
                                },
                             --Группа
                                {
                                'O7AI13', 'BERTSCH_MOZ_GW1AO13'
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'В дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'В танки BERTSCH',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_LINE',
                                },
                            [ 4 ] =
                                {
                                name = 'В танк №2 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_TANK',
                                },
                            [ 5 ] =
                                {
                                name = 'В танк №3 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 6 ] =
                                {
                                name = 'В танк №4 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 7 ] =
                                {
                                name = 'В танк №5 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 8 ] =
                                {
                                name = 'Запрос проталкивания',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'O7DO12'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'O7DI14', 'BERTSCH_MOZ_GW1DO14' }, 0, },
                                    },
                                enable_step_by_signal = --Сигнал для включения текущего шага
                                    {
                                    { 'BERTSCH_MOZ_GW1DI14' },
                                    false,
                                    },
                                },
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Наполнение в Ультрафильтрации',
                states =
                    {
                    [ 0 ] =
                        {
                        --'Простой'
                        jump_if = --Переход к состоянию по условию
                            {
                            --Группа
                                {
                                on_devices = --Включение устройств
                                    {
                                    'UF1_O7DI12'
                                    },
                                next_state_n = 1, --К состоянию операции
                                },
                            },
                        },
                    [ 1 ] =
                        {
                        --'Выполнение'
                        jump_if = --Переход к состоянию по условию
                            {
                            --Группа
                                {
                                off_devices = --Выключение устройств
                                    {
                                    'UF1_O7DI12'
                                    },
                                next_state_n = 3, --К состоянию операции
                                },
                            },
                        },
                    [ 3 ] =
                        {
                        --'Остановка'
                        jump_if = --Переход к состоянию по условию
                            {
                            --Группа
                                {
                                off_devices = --Выключение устройств
                                    {
                                    'UF1_O7DI12'
                                    },
                                next_state_n = 0, --К состоянию операции
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = 'O7FQT1',
            },
        },
    [ 44 ] =
        {
        n          = 8,
        tech_type  = 33,
        name       = 'Линия наполнения O',
        name_eplan = 'O',
        name_BC    = 'O8LineInObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_in',
        attached_objects = '41',
        tank_groups =
            {
                tanks = '20',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Время мойки основной линии',
                value = 600,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH'
                },
            [ 4 ] =
                {
                name = 'Время промывки седел клапанов',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_SED'
                },
            [ 5 ] =
                {
                name = 'Время промывки дренажа',
                value = 2,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_DRAINAGE'
                },
            [ 6 ] =
                {
                name = 'Время дренажа после мойки',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_DRAINAGE'
                },
            [ 7 ] =
                {
                name = 'Флаг использования бачка лимонной кислоты',
                value = 0,
                meter = '0/1',
                oper = { -1 },
                nameLua = 'ACTIVITY_TANK'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 10 ] =
                {
                name = 'Текущий приемник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_DESTINATION'
                },
            [ 11 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'WATER_FLAG'
                },
            [ 12 ] =
                {
                name = 'Принятый объем продукта',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 13 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Электропроводность основы',
                value = 3,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'CONCENTRATION'
                },
            [ 16 ] =
                {
                name = 'Дельта электропроводности основы',
                value = 0.2,
                meter = 'мСм/см',
                oper = { 2 },
                nameLua = 'D_CONCENTRATION'
                },
            [ 17 ] =
                {
                name = 'Время отсутствия расхода для завершения наполнения',
                value = 60,
                meter = 'с',
                oper = { 2 },
                nameLua = 'NO_FLOW_TIME'
                },
            [ 18 ] =
                {
                name = 'Минимальный расход для завершения дренажа',
                value = 0.4,
                meter = 'м куб./ч',
                oper = { 2 },
                nameLua = 'MIN_FLOW'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_END = 'O8DI2',
                    IGNORE_WATER_FLAG = 'false',
                    NEED_FLOW_CONTROL = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'LA_TANK1V102'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BERTSCH_MOZ_GW1DI21'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 3,
                                next_step_n = 2,
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI21', 'O8DO1' }, 0, },
                                    { { 'O8DI1', 'BERTSCH_MOZ_GW1DO21' }, 0, },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Промывка седел',
                                time_param_n = 4,
                                next_step_n = 3,
                                opened_lower_seat_v = --Нижние седла
                                    {
                                     --Группа
                                        {
                                        'LA_TANK1V102'
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI21', 'O8DO1' }, 0, },
                                    { { 'O8DI1', 'BERTSCH_MOZ_GW1DO21' }, 0, },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Промывка дренажа',
                                time_param_n = 5,
                                next_step_n = 1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'O8DO2'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI21', 'O8DO1' }, 0, },
                                    { { 'O8DI1', 'BERTSCH_MOZ_GW1DO21' }, 0, },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 6,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    TOTAL_VOLUME_AI = 'O8AI13',
                    MIN_FLOW = 'MIN_FLOW',
                    CONCENTRATION = 'CONCENTRATION',
                    DELTA_CONCENTRATION = 'D_CONCENTRATION',
                    NO_FLOW_TIME = 'NO_FLOW_TIME',
                    IS_END_ON_FULL_TANK = 'false',
                    MOVE_TO_STEP_WAITING_BY_SIGNALS = 'false',
                    NEED_PAUSE_AFTER_FULL_LAST_TANK = 'false',
                    CONTINUE_PRODUCT_PUSH = 'false',
                    NEED_FLOW_CONTROL = 'true',
                    NEED_PAUSE_FLOW_CONTROL = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        checked_devices = --Проверяемые устройства
                            {
                            'O8FQT1'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BERTSCH_MOZ_GW1DI31'
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'BERTSCH_MOZ_GW1DI32', 'O8DO11' }, 0, },
                            { { 'BERTSCH_MOZ_GW1DI34', 'O8DO12' }, 0, },
                            { { 'O8DI12', 'BERTSCH_MOZ_GW1DO33' }, 0, },
                            { { 'O8DI13', 'BERTSCH_MOZ_GW1DO32' }, 0, },
                            { { 'O8DI14', 'BERTSCH_MOZ_GW1DO34' }, 0, },
                            },
                        AI_AO = --Группы AI -> AO AO ...
                            {
                             --Группа
                                {
                                'BERTSCH_MOZ_GW1AI11', 'O8AO11'
                                },
                             --Группа
                                {
                                'O8AI14', 'BERTSCH_MOZ_GW1AO31'
                                },
                             --Группа
                                {
                                'O8AI13', 'BERTSCH_MOZ_GW1AO33'
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'В дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'В танки BERTSCH',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_LINE',
                                },
                            [ 4 ] =
                                {
                                name = 'В танк №2 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_TANK',
                                },
                            [ 5 ] =
                                {
                                name = 'В танк №3 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 6 ] =
                                {
                                name = 'В танк №4 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 7 ] =
                                {
                                name = 'В танк №5 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 8 ] =
                                {
                                name = 'Запрос проталкивания',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = 'O8FQT1',
            },
        },
    [ 45 ] =
        {
        n          = 3,
        tech_type  = 34,
        name       = 'Линия мойки',
        name_eplan = 'TANK',
        name_BC    = 'TankObj',
        cooper_param_number = -1,
        base_tech_object = 'CIP_node',
        tank_groups =
            {
                CIP_objects = '43',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка линии O7 Alpma+Bertsch',
                base_operation = 'WASHING_CIP',
                },
            },
        },
    [ 46 ] =
        {
        n          = 14,
        tech_type  = 35,
        name       = 'Линия W',
        name_eplan = 'W',
        name_BC    = 'W14LineOutObj1',
        cooper_param_number = -1,
        base_tech_object = 'line',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 4 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 5 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_REQUEST = 'BERTSCH_MOZ_GW1DI61',
                    IGNORE_WATER_FLAG = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'P4790V1'
                            },
                        opened_upper_seat_v = --Верхние седла
                            {
                             --Группа
                                {
                                'P4790V1'
                                },
                            },
                        required_FB = --Сигналы для включения
                            {
                            'BERTSCH_MOZ_GW1DI61'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DO = --DO
                                    {
                                    'W14DO11'
                                    },
                                },
                            },
                        DI_DO = --Группы DI -> DO DO ...
                            {
                            { { 'W14DI11', 'BERTSCH_MOZ_GW1DO61' }, 0, },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Выдача',
                base_operation = 'WORK',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        required_FB = --Сигналы для включения
                            {
                            'W14DI1'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Из BERTSCH',
                                time_param_n = -1,
                                next_step_n = -1,
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'W14DI1', 'BERTSCH_MOZ_GW1DO71' }, 0, },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Из ALPMA 4790',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'ALPMAGW5DI479013'
                                            },
                                        devices = --Устройства
                                            {
                                            'P4790V1', 'P4790V21'
                                            },
                                        },
                                    },
                                enable_step_by_signal = --Сигнал для включения текущего шага
                                    {
                                    { 'ALPMAGW5DI482010' },
                                    true,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = '',
            },
        },
    [ 47 ] =
        {
        n          = 1,
        tech_type  = 36,
        name       = 'Танк воды',
        name_eplan = 'WATER_TANK',
        name_BC    = 'WaterTankObj1',
        cooper_param_number = -1,
        base_tech_object = 'tank',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { 1,2,3,4 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { 1,2,3,4 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Ручной режим (операции управляются мастером (0) или вручную (1))',
                value = 0,
                meter = '0/1',
                oper = { 1,2,3,4 },
                nameLua = 'MASTER_MANUAL'
                },
            [ 4 ] =
                {
                name = 'Номер партии в танке',
                value = 1,
                meter = '№',
                oper = { 2,3,4 },
                nameLua = 'PART_NUMB1'
                },
            [ 5 ] =
                {
                name = 'Дата (день) производства партии в танке',
                value = 0,
                meter = 'д',
                oper = { 2,3,4 },
                nameLua = 'PART_DAY1'
                },
            [ 6 ] =
                {
                name = 'Дата (месяц) производства партии в танке',
                value = 0,
                meter = 'мес',
                oper = { 2,3,4 },
                nameLua = 'PART_MONTH1'
                },
            [ 7 ] =
                {
                name = 'Дата (год) производства партии в танке',
                value = 0,
                meter = 'г',
                oper = { 2,3,4 },
                nameLua = 'PART_YEAR1'
                },
            [ 8 ] =
                {
                name = 'Тип продукта',
                value = 0,
                meter = 'шт',
                oper = { 2,3,4 },
                nameLua = 'PRODUCT_TYPE'
                },
            [ 9 ] =
                {
                name = 'Номер линии наполнения',
                value = 0,
                meter = 'шт',
                oper = { 2 },
                nameLua = 'IN_LINE_OBJ_NUMBER'
                },
            [ 10 ] =
                {
                name = 'Номер линии выдачи',
                value = 0,
                meter = 'шт',
                oper = { 4 },
                nameLua = 'OUT_LINE_OBJ_NUMBER'
                },
            [ 11 ] =
                {
                name = 'Заданный объем',
                value = 1500000,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_SET'
                },
            [ 12 ] =
                {
                name = 'Текущий набранный объем',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_CURRENT'
                },
            [ 13 ] =
                {
                name = 'Заданный объем партии после мойки',
                value = 999999,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_ACCEPTING_SET_AFTER_CIP'
                },
            [ 14 ] =
                {
                name = 'Маска работающих линий наполнения',
                value = 0,
                meter = 'шт',
                oper = { 2,5 },
                nameLua = 'MASK_OF_WORKING_INLET_LINES'
                },
            [ 15 ] =
                {
                name = 'Маска работающих линий выдачи',
                value = 0,
                meter = 'шт',
                oper = { 4,5 },
                nameLua = 'MASK_OF_WORKING_OUTLET_LINES'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 18 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 21 ] =
                {
                name = 'Максимальный уровень для включения мойки',
                value = 1,
                meter = '%',
                oper = { 1 },
                nameLua = 'WASH_MAX_LT'
                },
            [ 22 ] =
                {
                name = 'Время шага мойки "На МГ"',
                value = 240,
                meter = 'c',
                oper = { 1 },
                nameLua = 'WASH_IN_TANK_TIME'
                },
            [ 23 ] =
                {
                name = 'Время шага мойки "Флипование под давлением"',
                value = 20,
                meter = 'c',
                oper = { 1 },
                nameLua = 'WASH_PRESSURE_FLUSH_TIME'
                },
            [ 24 ] =
                {
                name = 'Время шага мойки "Смена среды"',
                value = 120,
                meter = 'c',
                oper = { 1 },
                nameLua = 'WASH_MEDIUM_CHANGE_TIME'
                },
            [ 25 ] =
                {
                name = 'Время шага мойки "Объект опорожнен"',
                value = 3,
                meter = 'c',
                oper = { 1 },
                nameLua = 'WASH_OBJECT_EMPTY_TIME'
                },
            [ 26 ] =
                {
                name = 'Время шага мойки "Дренаж" после пропадания НУ',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME'
                },
            [ 27 ] =
                {
                name = 'Максимальное время шага мойки "Дренаж"',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'WASH_DRAINAGE_TIME_MAX'
                },
            [ 28 ] =
                {
                name = 'Максимальное время операции "Мойка"',
                value = 180,
                meter = 'мин',
                oper = { 1 },
                nameLua = 'WASH_TIME_MAX'
                },
            [ 29 ] =
                {
                name = 'Работа возвратного насоса CIP по уровню',
                value = 1,
                meter = '0/1',
                oper = { 1 },
                nameLua = 'OUT_PUMP_WASH_LS_WORK'
                },
            [ 30 ] =
                {
                name = 'Задержка включения возвратного насоса CIP',
                value = 10,
                meter = 'с',
                oper = { 1 },
                nameLua = 'OUT_PUMP_WASH_LS_DELAY'
                },
            [ 31 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 32 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 33 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 34 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 35 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 36 ] =
                {
                name = 'Заданная температура нагревания',
                value = 35,
                meter = 'град. C',
                oper = { 5 },
                nameLua = 'HEAT_TEMPERATURE'
                },
            [ 37 ] =
                {
                name = 'Дельта температуры',
                value = 1,
                meter = 'град. C',
                oper = { 5 },
                nameLua = 'HEAT_TEMPERATURE_DELTA'
                },
            [ 38 ] =
                {
                name = 'Время проверки температуры',
                value = 60,
                meter = 'с',
                oper = { 5 },
                nameLua = 'CHECK_TIME_HEAT_TEMPERATURE'
                },
            [ 39 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 40 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 41 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 42 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 43 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 44 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 45 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 46 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 47 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 48 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 49 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 50 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 51 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 52 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 53 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 54 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 55 ] =
                {
                name = 'Задержка выключения выдачи по НУ',
                value = 10,
                meter = 'сек',
                oper = { 4,5 },
                nameLua = 'DELAY_OUT_OFF_TIME'
                },
            [ 56 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 57 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 58 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 59 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 60 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },
        properties =
            {
            IGNORE_LS_DOWN = 'false',
            NO_CHECK_CURRENT_LEVEL = 'false',
            IGNORE_LEVELS_ERROR = 'false',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    MEDIUM_CHANGE_REQUEST = 'WLINE10DI3',
                    CIP_WASH_END = 'WLINE10DI4',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'WLINE10V1', 'WLINE10V2', 'WR1V1', 'WATER_TANK1V2', 'WATER_TANK1V3'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'WLINE10DI1'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DI = --DI
                                    {
                                    'WLINE10DI2'
                                    },
                                devices = --Устройства
                                    {
                                    'CIPM2'
                                    },
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'На МГ',
                                time_param_n = 22,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'WLINE10V11', 'WATER_TANK1V1', 'WATER_TANK1V14', 'WATER_TANK1V15', 'WATER_TANK1V16', 'WATER_TANK1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO1'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Флипование под давлением',
                                time_param_n = 23,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'WLINE10V11', 'WATER_TANK1V1', 'WATER_TANK1V14', 'WATER_TANK1V15', 'WATER_TANK1V16', 'WATER_TANK1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO1'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Смена среды',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'MEDIUM_CHANGE',
                                opened_devices = --Включать
                                    {
                                    'WATER_TANK1V1', 'WATER_TANK1V14', 'WATER_TANK1V15', 'WATER_TANK1V16'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'WLINE10V11', 'WATER_TANK1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO1'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Объект опорожнен',
                                time_param_n = 25,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'WLINE10V11', 'WATER_TANK1V1', 'WATER_TANK1V14', 'WATER_TANK1V15', 'WATER_TANK1V16', 'WATER_TANK1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO1'
                                            },
                                        },
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO3'
                                            },
                                        },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 27,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'WATER_TANK1V1', 'WLINE10V11', 'WATER_TANK1V14', 'WATER_TANK1V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'WATER_TANK1V15', 'WATER_TANK1V16'
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V2'
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    OPERATION_AFTER_FILL = '3',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'WATER_TANK1V1'
                            },
                        closed_devices = --Выключать
                            {
                            'WATER_TANK1V14', 'WATER_TANK1V11'
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        opened_devices = --Включать
                            {
                            'BRINE_TANK1V2'
                            },
                        },
                    },
                },
            [ 3 ] =
                {
                name = 'Хранение',
                base_operation = 'STORING',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'WATER_TANK1V1', 'WATER_TANK1V14', 'WATER_TANK1V11', 'WATER_TANK1V2', 'WATER_TANK1V3'
                            },
                        },
                    },
                },
            [ 4 ] =
                {
                name = 'Выдача',
                base_operation = 'OUT',
                props =
                    {
                    NEED_STORING_AFTER = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'WATER_TANK1V1'
                            },
                        closed_devices = --Выключать
                            {
                            'WATER_TANK1V14'
                            },
                        },
                    },
                },
            [ 5 ] =
                {
                name = 'Работа',
                base_operation = 'WORK',
                props =
                    {
                    WORK_FILL_AND_OUT = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        opened_devices = --Включать
                            {
                            'WATER_TANK1V1', 'WATER_TANK1V2', 'WATER_TANK1V3'
                            },
                        closed_devices = --Выключать
                            {
                            'WATER_TANK1V14', 'WATER_TANK1V11'
                            },
                        },
                    },
                },
            },
        equipment =
            {
            LS_up = 'WATER_TANK1LS2',
            hatch = 'WATER_TANK1GS1',
            hatch2 = '',
            LS_down = 'WATER_TANK1LS1',
            LT = 'WATER_TANK1LT1',
            TE = 'WATER_TANK1TE1',
            lamp = '',
            out_pump = 'CIPM2',
            },
        },
    [ 48 ] =
        {
        n          = 10,
        tech_type  = 37,
        name       = 'Линия наполнения WLINE',
        name_eplan = 'WLINE',
        name_BC    = 'WLINE10LineInObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_in',
        tank_groups =
            {
                tanks = '47',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время операции',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время шага',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '',
                oper = { 2 },
                nameLua = 'OPER_MODE'
                },
            [ 4 ] =
                {
                name = 'Текущий приемник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_DESTINATION'
                },
            [ 5 ] =
                {
                name = 'Принятый объем сыворотки',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 6 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '(1/0)',
                oper = { 2 },
                nameLua = 'WATER_FLAG'
                },
            [ 7 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Время шага мойки "Мойка линии"',
                value = 240,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH'
                },
            [ 12 ] =
                {
                name = 'Время шага мойки "Промывка седел"',
                value = 60,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_SED'
                },
            [ 13 ] =
                {
                name = 'Время шага мойки "Cнятие давления"',
                value = 1,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_REMOVE_PRESSURE'
                },
            [ 14 ] =
                {
                name = 'Время шага мойки "Промывка дренажа"',
                value = 6,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_DRAINAGE'
                },
            [ 15 ] =
                {
                name = 'Время шага мойки "Промывка дренажа - завершение"',
                value = 1,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_DRAINAGE_END'
                },
            [ 16 ] =
                {
                name = 'Время шага мойки "Дренаж"',
                value = 120,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_DRAINAGE'
                },
            [ 17 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 18 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 21 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 22 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 23 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_END = 'WLINE10DI4',
                    IGNORE_WATER_FLAG = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'WLINE10V1', 'WLINE10V2'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 11,
                                next_step_n = 2,
                                closed_devices = --Выключать
                                    {
                                    'WLINE10V12'
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Промывка седел',
                                time_param_n = 12,
                                next_step_n = 3,
                                closed_devices = --Выключать
                                    {
                                    'WLINE10V12'
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Cнятие давления',
                                time_param_n = 13,
                                next_step_n = 4,
                                closed_devices = --Выключать
                                    {
                                    'WLINE10V12'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO2'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Промывка дренажа',
                                time_param_n = 14,
                                next_step_n = 5,
                                opened_devices = --Включать
                                    {
                                    'WLINE10V12'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO2'
                                            },
                                        },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'Промывка дренажа - завершение',
                                time_param_n = 15,
                                next_step_n = 1,
                                closed_devices = --Выключать
                                    {
                                    'WLINE10V12'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO2'
                                            },
                                        },
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 16,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'WLINE10V12'
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Наполнение',
                base_operation = 'FILL',
                props =
                    {
                    TOTAL_VOLUME_AI = 'WLINE10AI13',
                    clean_water_DI = 'WLINE10DI12',
                    product_DI = 'WLINE10DI13',
                    IS_END_ON_FULL_TANK = 'false',
                    MOVE_TO_STEP_WAITING_BY_SIGNALS = 'false',
                    NEED_PAUSE_AFTER_FULL_LAST_TANK = 'true',
                    CONTINUE_PRODUCT_PUSH = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'WLINE10V11'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_KEY',
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO11'
                                            },
                                        },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'В дренаж',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'WLINE10V12'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO11'
                                            },
                                        },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'В танк №1',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'IN_TANK',
                                opened_devices = --Включать
                                    {
                                    'WLINE10V1'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO11'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'В танк №2 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO11'
                                            },
                                        },
                                    },
                                },
                            [ 5 ] =
                                {
                                name = 'В танк №3 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO11'
                                            },
                                        },
                                    },
                                },
                            [ 6 ] =
                                {
                                name = 'Проталкивание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'PRODUCT_PUSH',
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO11'
                                            },
                                        },
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WLINE10DO14'
                                            },
                                        },
                                    },
                                },
                            [ 7 ] =
                                {
                                name = 'Циркуляция',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'WLINE10V2'
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Пауза',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'По верхнему уровню в танке',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = 'WLINE10FQT1',
            },
        },
    [ 49 ] =
        {
        n          = 1,
        tech_type  = 38,
        name       = 'Линия выдачи воды WR',
        name_eplan = 'WR',
        name_BC    = 'WR1LineOutObj1',
        cooper_param_number = -1,
        base_tech_object = 'line_out',
        attached_objects = '50',
        tank_groups =
            {
                tanks = '47',
            },
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мсек',
                oper = { 1,2 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мсек',
                oper = { 1,2 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Режим работы операции, 0 - авто, 1 - ручной',
                value = 0,
                meter = '0/1',
                oper = { 1,2 },
                nameLua = 'OPER_MODE'
                },
            [ 4 ] =
                {
                name = 'Текущий источник, № - номер танка',
                value = 0,
                meter = '№',
                oper = { 2 },
                nameLua = 'OPER_SRC'
                },
            [ 5 ] =
                {
                name = 'Наличие воды/продукта в линии',
                value = 0,
                meter = '0/1',
                oper = { 1,2 },
                nameLua = 'WATER_FLAG'
                },
            [ 6 ] =
                {
                name = 'Выданный объем продукта',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'PROD_V'
                },
            [ 7 ] =
                {
                name = 'Использованный объем воды для проталкивания',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V'
                },
            [ 8 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 9 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 10 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 11 ] =
                {
                name = 'Время шага мойки "Мойка линии"',
                value = 300,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH'
                },
            [ 12 ] =
                {
                name = 'Время шага мойки "Промывка седел"',
                value = 20,
                meter = 'с',
                oper = { 1 },
                nameLua = 'TIME_WASH_SED'
                },
            [ 13 ] =
                {
                name = 'Время шага мойки "Дренаж"',
                value = 120,
                meter = 'сек',
                oper = { 1 },
                nameLua = 'TIME_DRAINAGE'
                },
            [ 14 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 15 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 16 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 17 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 18 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 19 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 20 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 21 ] =
                {
                name = 'Объем линии',
                value = 100,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_LINE'
                },
            [ 22 ] =
                {
                name = 'Дополнительный объем проталкивания в дренаж',
                value = 10,
                meter = 'л',
                oper = { 2 },
                nameLua = 'WATER_V_ADD'
                },
            [ 23 ] =
                {
                name = 'Требуемый объем выдачи',
                value = 0,
                meter = 'л',
                oper = { 2 },
                nameLua = 'V_LINE_OUT'
                },
            [ 24 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 25 ] =
                {
                name = 'Название параметра',
                value = 0,
                meter = 'шт',
                oper = { -1 },
                nameLua = 'P'
                },
            [ 26 ] =
                {
                name = 'Производительность насоса во время мойки',
                value = 80,
                meter = '%',
                oper = { 1 },
                nameLua = 'POWER_PUMP_CIP'
                },
            [ 27 ] =
                {
                name = 'Производительность насоса во время выдачи',
                value = 90,
                meter = '%',
                oper = { 2 },
                nameLua = 'POWER_PUMP_WORK'
                },
            [ 28 ] =
                {
                name = 'Заданный расход',
                value = 30,
                meter = 'м3/ч',
                oper = { 2 },
                nameLua = 'VOLUME_FLOW'
                },
            [ 29 ] =
                {
                name = 'Флаг использования нагревания, 0 - без нагревания, 1 - с нагреванием',
                value = 0,
                meter = '0/1',
                oper = { 2 },
                nameLua = 'HEATING_FLAG'
                },
            [ 30 ] =
                {
                name = 'Температура нагревания',
                value = 40,
                meter = 'град.C',
                oper = { 2 },
                nameLua = 'HEAT_TEMPERATURE'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка',
                base_operation = 'WASHING_CIP',
                props =
                    {
                    CIP_WASH_END = 'MCA6LINE2DI103',
                    IGNORE_WATER_FLAG = 'true',
                    NEED_HEATER_NODE = 'false',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        closed_devices = --Выключать
                            {
                            'WR1V1', 'WLINE10V2'
                            },
                        required_FB = --Сигналы для включения
                            {
                            'MCA6LINE2DI101', 'BERTSCH_MOZ_GW1DI41'
                            },
                        devices_data = --Устройства
                            {
                             --Группа
                                {
                                DI = --DI
                                    {
                                    'MCA6LINE2DI102'
                                    },
                                devices = --Устройства
                                    {
                                    'WR1M1'
                                    },
                                pump_freq = 26,
                                },
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Мойка линии',
                                time_param_n = 11,
                                next_step_n = 2,
                                opened_devices = --Включать
                                    {
                                    'WR1V31', 'WR1V32', 'WR1V33', 'WR1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BERTSCH_MOZ_GW1DO41'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI41', 'MCA6LINE2DO111' }, 0, },
                                    { { 'MCA6LINE2DI106', 'BERTSCH_MOZ_GW1DO42' }, 0, },
                                    { { 'MCA6LINE2DI105', 'BERTSCH_MOZ_GW1DO43' }, 0, },
                                    },
                                },
                            [ 2 ] =
                                {
                                name = 'Промывка седел',
                                time_param_n = 12,
                                next_step_n = 1,
                                opened_devices = --Включать
                                    {
                                    'WR1V31', 'WR1V32', 'WR1V33', 'WR1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BERTSCH_MOZ_GW1DO41'
                                            },
                                        },
                                    },
                                DI_DO = --Группы DI -> DO DO ...
                                    {
                                    { { 'BERTSCH_MOZ_GW1DI41', 'MCA6LINE2DO111' }, 0, },
                                    { { 'MCA6LINE2DI106', 'BERTSCH_MOZ_GW1DO42' }, 0, },
                                    { { 'MCA6LINE2DI105', 'BERTSCH_MOZ_GW1DO43' }, 0, },
                                    },
                                },
                            [ 3 ] =
                                {
                                name = 'Дренаж',
                                time_param_n = 13,
                                next_step_n = -1,
                                baseStep = 'DRAINAGE',
                                opened_devices = --Включать
                                    {
                                    'WR1V33', 'WR1V11'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'WR1V31', 'WR1V32'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'BERTSCH_MOZ_GW1DO44'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            [ 2 ] =
                {
                name = 'Выдача',
                base_operation = 'OUT',
                props =
                    {
                    product_DO = 'BERTSCH_MOZ_GW1DO53',
                    product_request = 'BERTSCH_MOZ_GW1DI52',
                    USE_VOLUME = 'false',
                    CONTINUE_WATER_PUSH = 'false',
                    NEED_PAUSE_AFTER_EMPTY_LAST_TANK = 'false',
                    WAITING_WATER_REQUEST = 'false',
                    NEED_HEATER_NODE = 'true',
                    HEATING_TEMPERATURE = 'HEAT_TEMPERATURE',
                    NEED_PAUSE_HEATER_NODE = 'true',
                    },
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        checked_devices = --Проверяемые устройства
                            {
                            'HEATER1M1'
                            },
                        closed_devices = --Выключать
                            {
                            'WR1V33'
                            },
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING_KEY',
                                },
                            [ 2 ] =
                                {
                                name = 'Проталкивание',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 3 ] =
                                {
                                name = 'Из танка №1',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'OUT_TANK',
                                opened_devices = --Включать
                                    {
                                    'WR1V1', 'WR1V11'
                                    },
                                required_FB = --Сигналы для включения
                                    {
                                    'BERTSCH_MOZ_GW1DI51'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'BERTSCH_MOZ_GW1DI52'
                                            },
                                        devices = --Устройства
                                            {
                                            'WR1M1'
                                            },
                                        },
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'BERTSCH_MOZ_GW1DI52'
                                            },
                                        devices = --Устройства
                                            {
                                            'WR1FC1'
                                            },
                                        pump_freq = 28,
                                        },
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WR1DO11'
                                            },
                                        },
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Из танка №2 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 5 ] =
                                {
                                name = 'Из танка №3 (Резерв)',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 6 ] =
                                {
                                name = 'Циркуляция',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'WR1V1'
                                    },
                                closed_devices = --Выключать
                                    {
                                    'WR1V11'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        devices = --Устройства
                                            {
                                            'WR1M1'
                                            },
                                        },
                                     --Группа
                                        {
                                        devices = --Устройства
                                            {
                                            'WR1FC1'
                                            },
                                        pump_freq = 28,
                                        },
                                     --Группа
                                        {
                                        DO = --DO
                                            {
                                            'WR1DO12'
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    [ 2 ] =
                        {
                        --'Пауза'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Пауза',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            [ 2 ] =
                                {
                                name = 'По нижнему уровню в танке',
                                time_param_n = -1,
                                next_step_n = -1,
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            QT = '',
            product_CTR = 'WR1FQT1',
            },
        },
    [ 50 ] =
        {
        n          = 1,
        tech_type  = 39,
        name       = 'Узел нагревания Линия воды WR',
        name_eplan = 'HEATER',
        name_BC    = 'HEATER1HeatObj1',
        cooper_param_number = -1,
        base_tech_object = 'heater_node',
        par_float =
            {
            [ 1 ] =
                {
                name = 'Время активной операции',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'OPERATION_TIME'
                },
            [ 2 ] =
                {
                name = 'Время активного шага',
                value = 0,
                meter = 'мс',
                oper = { -1 },
                nameLua = 'STEP_TIME'
                },
            [ 3 ] =
                {
                name = 'Температура нагревания продукта',
                value = 40,
                meter = 'град. C',
                oper = { 1 },
                nameLua = 'HEAT_TEMPERATURE'
                },
            [ 4 ] =
                {
                name = 'Дельта температуры нагревания продукта',
                value = 2,
                meter = 'град. C',
                oper = { 1 },
                nameLua = 'TE_HEAT_DELTA'
                },
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Нагревание',
                base_operation = 'HEATING',
                states =
                    {
                    [ 1 ] =
                        {
                        --'Выполнение'
                        steps =
                            {
                            [ 1 ] =
                                {
                                name = 'Ожидание',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WAITING',
                                },
                            [ 2 ] =
                                {
                                name = 'Работа',
                                time_param_n = -1,
                                next_step_n = -1,
                                baseStep = 'WORKING',
                                },
                            [ 3 ] =
                                {
                                name = 'Нагревание для BERTSCH',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'HEATER1M1', 'HEATER1V1'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'BERTSCH_MOZ_GW1DI52'
                                            },
                                        devices = --Устройства
                                            {
                                            'HEATER1TC2'
                                            },
                                        pump_freq = 3,
                                        },
                                     --Группа
                                        {
                                        DI = --DI
                                            {
                                            'BERTSCH_MOZ_GW1DI52'
                                            },
                                        devices = --Устройства
                                            {
                                            'HEATER1TC1'
                                            },
                                        pump_freq = 'HEATER1TC2',
                                        },
                                    },
                                enable_step_by_signal = --Сигнал для включения текущего шага
                                    {
                                    { 'WR1DI11' },
                                    true,
                                    },
                                },
                            [ 4 ] =
                                {
                                name = 'Нагревание для циркуляции',
                                time_param_n = -1,
                                next_step_n = -1,
                                opened_devices = --Включать
                                    {
                                    'HEATER1M1', 'HEATER1V1'
                                    },
                                devices_data = --Устройства
                                    {
                                     --Группа
                                        {
                                        devices = --Устройства
                                            {
                                            'HEATER1TC1'
                                            },
                                        },
                                     --Группа
                                        {
                                        devices = --Устройства
                                            {
                                            'HEATER1TC2'
                                            },
                                        pump_freq = 3,
                                        },
                                    },
                                enable_step_by_signal = --Сигнал для включения текущего шага
                                    {
                                    { 'WR1DI12' },
                                    true,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        equipment =
            {
            TE = 'HEATER1TE2',
            },
        },
    [ 51 ] =
        {
        n          = 4,
        tech_type  = 2,
        name       = 'Мойка WLINE10+Танк воды №1',
        name_eplan = 'TANK',
        name_BC    = 'TankObj',
        cooper_param_number = -1,
        base_tech_object = 'CIP_node',
        tank_groups =
            {
                CIP_objects = '48 47',
            },

        modes =
            {
            [ 1 ] =
                {
                name = 'Мойка WLINE10+Танк воды №1',
                base_operation = 'WASHING_CIP',
                },
            },
        },
    }
end
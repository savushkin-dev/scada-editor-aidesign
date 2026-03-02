--version  = 1
------------------------------------------------------------------------------
PAC_name       = 'O1-Моцарелла'
PAC_id         = '1259'
------------------------------------------------------------------------------
--Узлы IO
nodes =
    {
        {
        name    = 'A1',
        ntype   = 201, --AXC F 2152
        n       = 1,
        IP      = '10.216.98.90',
        modules =
            {
            }
        },
        {
        name    = 'A100',
        ntype   = 200, --AXL F BK ETH
        n       = 2,
        IP      = '10.216.98.91',
        modules =
            {
             { 2688527 },        --AXL F AO4 1H,
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688491 },        --AXL F AI4 I 1H,
             { 2688093 },        --AXL F CNT2 INC2 1F,
            }
        },
        {
        name    = 'A200',
        ntype   = 200, --AXL F BK ETH
        n       = 3,
        IP      = '10.216.98.92',
        modules =
            {
             { 2688527 },        --AXL F AO4 1H,
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
            }
        },
        {
        name    = 'A300',
        ntype   = 200, --AXL F BK ETH
        n       = 4,
        IP      = '10.216.98.93',
        modules =
            {
             { 2688527 },        --AXL F AO4 1H,
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688093 },        --AXL F CNT2 INC2 1F,
            }
        },
        {
        name    = 'A400',
        ntype   = 200, --AXL F BK ETH
        n       = 5,
        IP      = '10.216.98.94',
        modules =
            {
             { 2688527 },        --AXL F AO4 1H,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688048 },        --AXL F DO16/3 2F,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 1027843 },        --AXL F IOL8 2H,
            }
        },
        {
        name    = 'A500',
        ntype   = 200, --AXL F BK ETH
        n       = 6,
        IP      = '10.216.98.95',
        modules =
            {
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 1027843 },        --AXL F IOL8 2H,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688022 },        --AXL F DI16/4 2F,
             { 2688491 },        --AXL F AI4 I 1H,
             { 2688093 },        --AXL F CNT2 INC2 1F,
            }
        },
    }
------------------------------------------------------------------------------
--Устройства
devices =
    {
        {
        name    = 'BRINE_TANK1V1',
        descr   = 'Донный клапан',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1110,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                8,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V11',
        descr   = 'CIP+ на МГ',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1112,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                10,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V12',
        descr   = 'Рассол. возврат в танк',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1113,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                9,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V13',
        descr   = 'Рассол. наполнение. в танк',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1114,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                12,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V14',
        descr   = 'Отсечной (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1115,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                11,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V15',
        descr   = 'Отсечной (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1116,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                14,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V2',
        descr   = 'Дренаж (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1111,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                7,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V21',
        descr   = 'Рассол -> Танк',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 4,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 4,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BRINE_TANK1V22',
        descr   = 'BV 26-2.2 4885 -> Рассол',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 4,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 4,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V1',
        descr   = 'Донный клапан',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1124,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                22,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 5,
                offset        = 9,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 0
                },
            },
        AI =
            {
                {
                node          = 5,
                offset        = 9,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 0
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V13',
        descr   = 'CIP+. Труба продукта',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1120,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                18,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V14',
        descr   = 'CIP+. Бункер продукта',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1121,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                17,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V15',
        descr   = 'CIP+. Бункер автомата',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1122,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                20,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1123,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                19,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V17',
        descr   = 'CIP-/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 5,
                offset        = 11,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 0
                },
            },
        AI =
            {
                {
                node          = 5,
                offset        = 11,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 0
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V2',
        descr   = 'Дренаж',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1125,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                21,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V21',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 576,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1136,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1137,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V22',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 577,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1138,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1139,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V23',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 578,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1140,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1141,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V24',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 579,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1142,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1143,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V25',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 580,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1144,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1145,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V26',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 581,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1146,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1147,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V27',
        descr   = 'Клапан. моющей головки',
        dtype   = 0,
        subtype = 5, -- V_DO1_DI2
        article = 'GEA.TM15P2BAM',
        DO =
            {
                {
                node          = 4,
                offset        = 582,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 0
                },
            },
        DI =
            {
                {
                -- Открыт
                node          = 4,
                offset        = 1148,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 1136
                },
                {
                -- Закрыт
                node          = 4,
                offset        = 1149,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 1136
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V40',
        descr   = 'Сетевая вода (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1127,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                23,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V43',
        descr   = 'Подготовленная вода. выход к 4790 (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2075,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                27,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V5',
        descr   = 'Циркуляция',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1128,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                26,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'BUNKER1V6',
        descr   = 'Подача в бункер',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1126,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                24,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'CIPV1',
        descr   = 'CIP+. Магистральный (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2076,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                30,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'CIPV3',
        descr   = 'CIP+. Магистральный (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2077,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                29,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'CIPV7',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1624,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                26,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V1',
        descr   = 'Донный клапан',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1615,
                physical_port = 47,
                logical_port  = 16,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                15,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {4000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V11',
        descr   = 'CIP+ (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1616,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                18,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V12',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1617,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                17,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V14',
        descr   = 'CIP+. Промывка трубы. наполнения',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1619,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                19,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V15',
        descr   = 'CIP+. На МГ',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1620,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                22,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V16',
        descr   = 'CIP+. В байпас',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1621,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                21,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V17',
        descr   = 'Дренаж',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1622,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                24,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'COAG1V26',
        descr   = 'Вход пара',
        dtype   = 0,
        subtype = 12, -- V_IOLINK_VTUG_DO1
        article = '',
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                32,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        },

        {
        name    = 'F_BRINE_IN1V1',
        descr   = 'Вода -> Танк №1',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2071,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                23,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_IN1V2',
        descr   = 'Вода -> Танк №2',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2072,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                26,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_IN1V41',
        descr   = 'Подготовленная вода. выход к PFM (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2073,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                25,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_IN1V42',
        descr   = 'Подготовленная вода. дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2074,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                28,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V1',
        descr   = 'Танк №1 -> PFM №1',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 5,
                offset        = 3,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 0
                },
            },
        AI =
            {
                {
                node          = 5,
                offset        = 3,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 0
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V11',
        descr   = 'CIP+ (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2065,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                17,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V12',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2066,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                20,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V13',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2067,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                19,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V15',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2068,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                22,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V16',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2069,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                21,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V17',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2070,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                24,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V2',
        descr   = 'Танк №2 -> PFM №1',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 5,
                offset        = 5,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 0
                },
            },
        AI =
            {
                {
                node          = 5,
                offset        = 5,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 0
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V3',
        descr   = 'Выдача',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 5,
                offset        = 7,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 0
                },
            },
        AI =
            {
                {
                node          = 5,
                offset        = 7,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 0
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_OUT1V4',
        descr   = 'Циркуляция (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2064,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 2064
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                18,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V1',
        descr   = 'Донный клапан',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2048,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                2,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V11',
        descr   = 'CIP+ (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2049,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                1,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V12',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2050,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                4,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V13',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2051,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                3,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V15',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2052,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                6,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V16',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2053,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                5,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V17',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2054,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                8,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK1V21',
        descr   = 'Вход лед.воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2055,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                7,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V1',
        descr   = 'Донный клапан',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2056,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                10,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V11',
        descr   = 'CIP+ (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2057,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                9,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V12',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2058,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                12,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V13',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2059,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                11,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V15',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2060,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                14,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V16',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2061,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                13,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V17',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2062,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                16,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'F_BRINE_TANK2V21',
        descr   = 'Вход лед.воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2063,
                physical_port = 47,
                logical_port  = 16,
                module_offset = 2048
                },
            },
        AO =
            {
                {
                node          = 5,
                offset        = 67,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 64
                },
            },
        rt_par = 
                {
                15,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V1',
        descr   = 'Донный клапан',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1600,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                2,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V101',
        descr   = 'Бачок лимонной кислоты №1.  -> GMZ1',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 1,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 1,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V11',
        descr   = 'CIP+ (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1604,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                6,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V12',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1605,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                5,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V13',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1606,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                8,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V14',
        descr   = 'CIP+. Труба продукта',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1607,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                7,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V18',
        descr   = 'Дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1610,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                12,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V2',
        descr   = 'Отсечной (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1601,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                1,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V3',
        descr   = 'Отсечной (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1602,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                4,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'LA_TANK1V4',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1603,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                3,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'O7V121',
        descr   = 'O7 -> Сыроизготовитель №1',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 1,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 1,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'O7V34',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1612,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                14,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'O7V35',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1613,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                13,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'O7V36',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1614,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 1600
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                16,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4790V12',
        descr   = 'CIP+ (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1088,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                2,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4790V13',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1089,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                1,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4790V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1090,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                4,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4790V41',
        descr   = 'Сетевая вода.  вход',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1627,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                27,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4790V42',
        descr   = 'Сетевая вода.  дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1628,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                30,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4790V43',
        descr   = 'Сетевая вода.  вход (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 1,
                offset        = 1629,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 1616
                },
            },
        AO =
            {
                {
                node          = 1,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                29,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4805V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 2,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 2,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4805V12',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1088,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                2,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4805V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1089,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                1,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4805V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1090,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                4,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V1',
        descr   = 'HWP 4790. -> WCSLE-2000/A 4820',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 3,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 7,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 3,
                offset        = 11,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 11,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V12',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1091,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                3,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V13',
        descr   = 'Отсечной (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1092,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                6,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1093,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                5,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1094,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                8,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V19',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1096,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                10,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V2',
        descr   = 'WCSLE-2000/A 4820. -> HWP 4790',
        dtype   = 0,
        subtype = 15, -- V_IOLINK_MIXPROOF
        article = 'AL.9615-4003-06',
        AO =
            {
                {
                node          = 3,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V36',
        descr   = 'Вход. подогревающей. воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1097,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                9,      --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4820V37',
        descr   = 'Вход. подогревающей. воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1098,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                12,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4835V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 2,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 2,
                offset        = 9,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4835V12',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1092,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                6,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4835V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1093,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                5,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4835V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1094,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                8,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4835V36',
        descr   = 'Вход. подогревающей. воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1096,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                10,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 2,
                offset        = 11,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 2,
                offset        = 11,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V12',
        descr   = 'CIP+. Маршрут №1',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1097,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                9,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V13',
        descr   = 'CIP+. Маршрут №2',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1098,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                12,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1099,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                11,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1103,
                physical_port = 47,
                logical_port  = 16,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                15,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V18',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1100,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                14,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V20',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1101,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                13,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V21',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1102,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                16,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V3',
        descr   = 'CIP-/Циркуляция',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 2,
                offset        = 13,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 2,
                offset        = 13,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V31',
        descr   = 'Лед.вода. вход',
        dtype   = 0,
        subtype = 12, -- V_IOLINK_VTUG_DO1
        article = '',
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                17,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        },

        {
        name    = 'P4840V36',
        descr   = 'Вход. подогревающей. воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1104,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                18,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V41',
        descr   = 'Сетевая вода.  вход',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1106,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                20,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V42',
        descr   = 'Сетевая вода.  дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1108,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                22,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4840V43',
        descr   = 'Сетевая вода.  вход (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1107,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                19,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 3,
                offset        = 13,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 13,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V12',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1099,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                11,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V13',
        descr   = 'Отсечной (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 2,
                offset        = 1109,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 2,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                21,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1101,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                13,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1102,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 1088
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                16,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V36',
        descr   = 'Вход. подогревающей. воды',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1104,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                18,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V41',
        descr   = 'Сетевая вода.  вход',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1111,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                23,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V42',
        descr   = 'Сетевая вода.  дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1125,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                37,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4850V43',
        descr   = 'Сетевая вода.  вход (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1120,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                34,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 3,
                offset        = 17,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 17,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V12',
        descr   = 'CIP+',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1105,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                17,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1106,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                20,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1109,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                21,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V20',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1107,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                19,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V21',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1108,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                22,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V3',
        descr   = 'CIP-/Циркуляция',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 3,
                offset        = 15,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 15,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V31',
        descr   = 'Лед.вода. вход',
        dtype   = 0,
        subtype = 12, -- V_IOLINK_VTUG_DO1
        article = '',
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                36,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        },

        {
        name    = 'P4870V41',
        descr   = 'Сетевая вода.  вход',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1110,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                24,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V42',
        descr   = 'Сетевая вода.  дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1126,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                40,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4870V43',
        descr   = 'Сетевая вода.  вход (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1112,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                26,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 3,
                offset        = 21,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 21,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V12',
        descr   = 'CIP+. Маршрут №1',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1113,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                25,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V13',
        descr   = 'CIP+. Маршрут №2',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1114,
                physical_port = 42,
                logical_port  = 11,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                28,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1115,
                physical_port = 43,
                logical_port  = 12,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                27,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1118,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                32,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V19',
        descr   = 'CIP-. Бункер',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1124,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                38,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V20',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1116,
                physical_port = 44,
                logical_port  = 13,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                30,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V21',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1117,
                physical_port = 45,
                logical_port  = 14,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                29,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V3',
        descr   = 'CIP-/Циркуляция',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 3,
                offset        = 19,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 3,
                offset        = 19,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V31',
        descr   = 'Лед.вода. вход',
        dtype   = 0,
        subtype = 12, -- V_IOLINK_VTUG_DO1
        article = '',
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                35,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        },

        {
        name    = 'P4875V41',
        descr   = 'Сетевая вода.  вход',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1119,
                physical_port = 47,
                logical_port  = 16,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                31,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V42',
        descr   = 'Сетевая вода.  дренаж (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1127,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                39,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4875V43',
        descr   = 'Сетевая вода.  вход (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 3,
                offset        = 1121,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1120
                },
            },
        AO =
            {
                {
                node          = 3,
                offset        = 39,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 36
                },
            },
        rt_par = 
                {
                33,     --R_VTUG_NUMBER
                3,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V11',
        descr   = 'CIP+/Дренаж',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 4,
                offset        = 13,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 4,
                offset        = 13,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V12',
        descr   = 'CIP+. Маршрут №1',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1104,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                2,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V13',
        descr   = 'CIP+. Маршрут №2',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1105,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                1,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V16',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1106,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                4,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V17',
        descr   = 'CIP- (NO)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1109,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                5,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V20',
        descr   = 'CIP- (NC)',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1107,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                3,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V21',
        descr   = 'CIP-',
        dtype   = 0,
        subtype = 13, -- V_IOLINK_VTUG_DO1_FB_OFF
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1108,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1104
                },
            },
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                6,      --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        par = {5000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V3',
        descr   = 'CIP-/Циркуляция',
        dtype   = 0,
        subtype = 16, -- V_IOLINK_DO1_DI2
        article = 'AL.9615-4003-08',
        AO =
            {
                {
                node          = 4,
                offset        = 11,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        AI =
            {
                {
                node          = 4,
                offset        = 11,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        par = {10000 --[[P_ON_TIME]], 1 --[[P_FB]] }
        },

        {
        name    = 'P4885V31',
        descr   = 'Лед.вода. вход',
        dtype   = 0,
        subtype = 12, -- V_IOLINK_VTUG_DO1
        article = '',
        AO =
            {
                {
                node          = 4,
                offset        = 40,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 37
                },
            },
        rt_par = 
                {
                13,     --R_VTUG_NUMBER
                2,      --R_VTUG_SIZE
                },
        },

        {
        name    = 'P4840VC1',
        descr   = 'Регулирующий клапан',
        dtype   = 1,
        subtype = 1, -- VC
        article = '',
        AO =
            {
                {
                node          = 2,
                offset        = 0,
                physical_port = 10,
                logical_port  = 1,
                module_offset = 0
                },
            },
        },

        {
        name    = 'P4870VC1',
        descr   = 'Регулирующий клапан',
        dtype   = 1,
        subtype = 1, -- VC
        article = '',
        AO =
            {
                {
                node          = 3,
                offset        = 0,
                physical_port = 10,
                logical_port  = 1,
                module_offset = 0
                },
            },
        },

        {
        name    = 'P4875VC1',
        descr   = 'Регулирующий клапан',
        dtype   = 1,
        subtype = 1, -- VC
        article = '',
        AO =
            {
                {
                node          = 3,
                offset        = 1,
                physical_port = 11,
                logical_port  = 2,
                module_offset = 0
                },
            },
        },

        {
        name    = 'P4885VC1',
        descr   = 'Регулирующий клапан',
        dtype   = 1,
        subtype = 1, -- VC
        article = '',
        AO =
            {
                {
                node          = 4,
                offset        = 0,
                physical_port = 10,
                logical_port  = 1,
                module_offset = 0
                },
            },
        },

        {
        name    = 'BRINE_TANK1M1',
        descr   = 'Насос циркуляции/CIP-',
        dtype   = 2,
        subtype = 9, -- M_ATV
        article = '',
        prop = --Дополнительные свойства
            {
            IP = '10.216.98.104',
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'BUNKER1M1',
        descr   = 'Насос циркуляции/CIP-',
        dtype   = 2,
        subtype = 9, -- M_ATV
        article = '',
        prop = --Дополнительные свойства
            {
            IP = '10.216.98.103',
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'F_BRINE_OUT1M1',
        descr   = 'Возврат мойки',
        dtype   = 2,
        subtype = 9, -- M_ATV
        article = '',
        prop = --Дополнительные свойства
            {
            IP = '10.216.98.98',
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'F_BRINE_OUT1M2',
        descr   = 'Насос продукта',
        dtype   = 2,
        subtype = 9, -- M_ATV
        article = '',
        prop = --Дополнительные свойства
            {
            IP = '10.216.98.99',
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'F_BRINE_TANK1M1',
        descr   = 'Мешалка',
        dtype   = 2,
        subtype = 1, -- M
        article = '',
        DO =
            {
                {
                -- Пуск
                node          = 5,
                offset        = 528,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 32
                },
            },
        DI =
            {
                {
                -- Обратная связь
                node          = 5,
                offset        = 2080,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 2080
                },
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'F_BRINE_TANK2M1',
        descr   = 'Мешалка',
        dtype   = 2,
        subtype = 1, -- M
        article = '',
        DO =
            {
                {
                -- Пуск
                node          = 5,
                offset        = 529,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 32
                },
            },
        DI =
            {
                {
                -- Обратная связь
                node          = 5,
                offset        = 2081,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 2080
                },
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'LA_TANK1M1',
        descr   = 'Мешалка',
        dtype   = 2,
        subtype = 9, -- M_ATV
        article = '',
        prop = --Дополнительные свойства
            {
            IP = '10.216.98.101',
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'LA_TANK1M2',
        descr   = 'Возврат мойки',
        dtype   = 2,
        subtype = 1, -- M
        article = '',
        DO =
            {
                {
                -- Пуск
                node          = 1,
                offset        = 82,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 4
                },
            },
        DI =
            {
                {
                -- Обратная связь
                node          = 1,
                offset        = 1105,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 68
                },
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'LA_TANK1M3',
        descr   = 'Насос-дозатор',
        dtype   = 2,
        subtype = 2, -- M_FREQ
        article = '',
        DO =
            {
                {
                -- Пуск
                node          = 1,
                offset        = 83,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 4
                },
            },
        DI =
            {
                {
                -- Обратная связь
                node          = 1,
                offset        = 1106,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 68
                },
            },
        AO =
            {
                {
                -- Частота вращения
                node          = 1,
                offset        = 0,
                physical_port = 10,
                logical_port  = 1,
                module_offset = 0
                },
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'W2M1',
        descr   = 'Насос сыворотки/CIP-',
        dtype   = 2,
        subtype = 9, -- M_ATV
        article = '',
        prop = --Дополнительные свойства
            {
            IP = '10.216.98.102',
            },
        par = {2000 --[[P_ON_TIME]] }
        },

        {
        name    = 'BRINE_TANK1LS1',
        descr   = 'Нижний уровень',
        dtype   = 3,
        subtype = 3, -- LS_IOLINK_MIN
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 4,
                offset        = 44,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 37
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'BRINE_TANK1LS2',
        descr   = 'Верхний уровень',
        dtype   = 3,
        subtype = 4, -- LS_IOLINK_MAX
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 4,
                offset        = 45,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 37
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'BUNKER1LS1',
        descr   = 'Бункер автомата. Нижний уровень',
        dtype   = 3,
        subtype = 3, -- LS_IOLINK_MIN
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 5,
                offset        = 101,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 96
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'BUNKER1LS2',
        descr   = 'Бункер автомата. Верхний уровень',
        dtype   = 3,
        subtype = 4, -- LS_IOLINK_MAX
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 5,
                offset        = 102,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 96
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'F_BRINE_TANK1LS1',
        descr   = 'Нижний уровень',
        dtype   = 3,
        subtype = 3, -- LS_IOLINK_MIN
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 5,
                offset        = 70,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 64
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'F_BRINE_TANK1LS2',
        descr   = 'Верхний уровень',
        dtype   = 3,
        subtype = 4, -- LS_IOLINK_MAX
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 5,
                offset        = 71,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 64
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'F_BRINE_TANK2LS1',
        descr   = 'Нижний уровень',
        dtype   = 3,
        subtype = 3, -- LS_IOLINK_MIN
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 5,
                offset        = 75,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 64
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'F_BRINE_TANK2LS2',
        descr   = 'Верхний уровень',
        dtype   = 3,
        subtype = 4, -- LS_IOLINK_MAX
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 5,
                offset        = 76,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 64
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'LA_TANK1LS1',
        descr   = 'Нижний уровень',
        dtype   = 3,
        subtype = 3, -- LS_IOLINK_MIN
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 1,
                offset        = 41,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 36
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'LA_TANK1LS2',
        descr   = 'Верхний уровень',
        dtype   = 3,
        subtype = 4, -- LS_IOLINK_MAX
        article = 'IFM.LMT100',
        AI =
            {
                {
                node          = 1,
                offset        = 42,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 36
                },
            },
        par = {1000 --[[P_DT]], 1000 --[[P_ERR]] }
        },

        {
        name    = 'BRINE_TANK1TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 4,
                offset        = 43,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 37
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'F_BRINE_TANK1TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 5,
                offset        = 69,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 64
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'F_BRINE_TANK2TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 5,
                offset        = 74,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 64
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'LA_TANK1TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 1,
                offset        = 45,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 36
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'P4840TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 2,
                offset        = 41,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 36
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'P4870TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 3,
                offset        = 42,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 36
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'P4875TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 3,
                offset        = 43,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 36
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'P4885TE1',
        descr   = 'Температура',
        dtype   = 4,
        subtype = 2, -- TE_IOLINK
        article = 'IFM.TA2435',
        AI =
            {
                {
                node          = 4,
                offset        = 42,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 37
                },
            },
        par = {0 --[[P_C0]], -1000 --[[P_ERR]] }
        },

        {
        name    = 'BRINE_TANK1GS1',
        descr   = 'Датчик. положения люка',
        dtype   = 6,
        subtype = 1, -- GS
        article = 'OMR.E2A-S18KS08-M1-B1',
        DI =
            {
                {
                node          = 4,
                offset        = 1150,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 1136
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'F_BRINE_TANK1GS1',
        descr   = 'Датчик. положения люка',
        dtype   = 6,
        subtype = 1, -- GS
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2088,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 2080
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'F_BRINE_TANK2GS1',
        descr   = 'Датчик. положения люка',
        dtype   = 6,
        subtype = 1, -- GS
        article = 'OMR.E2A-S12KS04-M1-B1',
        DI =
            {
                {
                node          = 5,
                offset        = 2089,
                physical_port = 41,
                logical_port  = 10,
                module_offset = 2080
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'F_BRINE_IN1FQT1',
        descr   = 'Преобразователь расхода',
        dtype   = 7,
        subtype = 2, -- FQT_F
        article = 'E&H.Promag 5H3B50-GRIBAEAFBAFDCS0BA1',
        AI =
            {
                {
                -- Объем
                node          = 5,
                offset        = 138,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 135
                },
                {
                -- Поток
                node          = 5,
                offset        = 131,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 131
                },
            },
        par = {0 --[[P_MIN_F]], 66 --[[P_MAX_F]], 0 --[[P_C0]], 8000 --[[P_DT]] }
        },

        {
        name    = 'LA_TANK1FQT1',
        descr   = 'Преобразователь расхода',
        dtype   = 7,
        subtype = 2, -- FQT_F
        article = 'E&H.Promag 5H3B02-GRIBAEAFBAFDCS0BA1',
        AI =
            {
                {
                -- Объем
                node          = 1,
                offset        = 141,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 138
                },
                {
                -- Поток
                node          = 1,
                offset        = 134,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 134
                },
            },
        par = {0 --[[P_MIN_F]], 200 --[[P_MAX_F]], 0 --[[P_C0]], 8000 --[[P_DT]] }
        },

        {
        name    = 'O7FQT1',
        descr   = 'Преобразователь расхода',
        dtype   = 7,
        subtype = 2, -- FQT_F
        article = 'E&H.Promag 5H3B50-GRIBAEAFBAFDCS0BA1',
        AI =
            {
                {
                -- Объем
                node          = 1,
                offset        = 143,
                physical_port = 4,
                logical_port  = 2,
                module_offset = 138
                },
                {
                -- Поток
                node          = 1,
                offset        = 135,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 134
                },
            },
        par = {0 --[[P_MIN_F]], 66 --[[P_MAX_F]], 0 --[[P_C0]], 8000 --[[P_DT]] }
        },

        {
        name    = 'P4850FQT1',
        descr   = 'Счетчик оборотов. барабана',
        dtype   = 7,
        subtype = 1, -- FQT
        article = 'OMR.E2A-S12KS04-M1-B1',
        AI =
            {
                {
                -- Объем
                node          = 5,
                offset        = 140,
                physical_port = 4,
                logical_port  = 2,
                module_offset = 135
                },
            },
        },

        {
        name    = 'BRINE_TANK1LT1',
        descr   = 'Текущий уровень',
        dtype   = 8,
        subtype = 5, -- LT_IOLINK
        article = 'IFM.PM1707',
        AI =
            {
                {
                node          = 4,
                offset        = 75,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 72
                },
            },
        par = {0 --[[P_C0]], 5000 --[[P_ERR]], 1 --[[P_MAX_P]], 0.91 --[[P_R]], 0.3 --[[P_H_CONE]] }
        },

        {
        name    = 'BUNKER1LT1',
        descr   = 'Текущий уровень',
        dtype   = 8,
        subtype = 5, -- LT_IOLINK
        article = 'IFM.PM1708',
        AI =
            {
                {
                node          = 5,
                offset        = 103,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 96
                },
            },
        par = {0 --[[P_C0]], 1000 --[[P_ERR]], 0.25 --[[P_MAX_P]], 0.5 --[[P_R]], 0 --[[P_H_CONE]] }
        },

        {
        name    = 'F_BRINE_TANK1LT1',
        descr   = 'Текущий уровень',
        dtype   = 8,
        subtype = 5, -- LT_IOLINK
        article = 'IFM.PM1708',
        AI =
            {
                {
                node          = 5,
                offset        = 72,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 64
                },
            },
        par = {0 --[[P_C0]], 4000 --[[P_ERR]], 0.25 --[[P_MAX_P]], 0.65 --[[P_R]], 0.27 --[[P_H_CONE]] }
        },

        {
        name    = 'F_BRINE_TANK2LT1',
        descr   = 'Текущий уровень',
        dtype   = 8,
        subtype = 5, -- LT_IOLINK
        article = 'IFM.PM1708',
        AI =
            {
                {
                node          = 5,
                offset        = 99,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 96
                },
            },
        par = {0 --[[P_C0]], 4000 --[[P_ERR]], 0.25 --[[P_MAX_P]], 0.65 --[[P_R]], 0.27 --[[P_H_CONE]] }
        },

        {
        name    = 'LA_TANK1LT1',
        descr   = 'Текущий уровень',
        dtype   = 8,
        subtype = 5, -- LT_IOLINK
        article = 'IFM.PM1708',
        AI =
            {
                {
                node          = 1,
                offset        = 43,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 36
                },
            },
        par = {0 --[[P_C0]], 700 --[[P_ERR]], 0.25 --[[P_MAX_P]], 0.4 --[[P_R]], 0 --[[P_H_CONE]] }
        },

        {
        name    = 'O7QT1',
        descr   = 'Преобразователь проводимости',
        dtype   = 9,
        subtype = 3, -- QT_IOLINK
        article = 'IFM.LDL100',
        AI =
            {
                {
                node          = 1,
                offset        = 46,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 36
                },
            },
        par = {1000 --[[P_ERR]] }
        },

        {
        name    = 'CAB1HA1',
        descr   = 'Аварийная сигнализация. Сирена',
        dtype   = 10,
        subtype = 1, -- HA
        article = 'PXC.2702997',
        DO =
            {
                {
                node          = 1,
                offset        = 1651,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 102
                },
            },
        },

        {
        name    = 'CAB2HA1',
        descr   = 'Аварийная сигнализация. Сирена',
        dtype   = 10,
        subtype = 1, -- HA
        article = 'PXC.2702997',
        DO =
            {
                {
                node          = 2,
                offset        = 599,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 36
                },
            },
        },

        {
        name    = 'CAB3HA1',
        descr   = 'Аварийная сигнализация. Сирена',
        dtype   = 10,
        subtype = 1, -- HA
        article = 'PXC.2702997',
        DO =
            {
                {
                node          = 3,
                offset        = 1155,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 71
                },
            },
        },

        {
        name    = 'CAB4HA1',
        descr   = 'Аварийная сигнализация. Сирена',
        dtype   = 10,
        subtype = 1, -- HA
        article = 'PXC.2702997',
        DO =
            {
                {
                node          = 4,
                offset        = 1171,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 72
                },
            },
        },

        {
        name    = 'CAB5HA1',
        descr   = 'Аварийная сигнализация. Сирена',
        dtype   = 10,
        subtype = 1, -- HA
        article = 'PXC.2702997',
        DO =
            {
                {
                node          = 5,
                offset        = 1559,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 96
                },
            },
        },

        {
        name    = 'CAB1HL1',
        descr   = 'Аварийная сигнализация. Зеленый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700119',
        DO =
            {
                {
                node          = 1,
                offset        = 1648,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 102
                },
            },
        },

        {
        name    = 'CAB1HL2',
        descr   = 'Аварийная сигнализация. Оранжевый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700122',
        DO =
            {
                {
                node          = 1,
                offset        = 1649,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 102
                },
            },
        },

        {
        name    = 'CAB1HL3',
        descr   = 'Аварийная сигнализация. Красный',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700115',
        DO =
            {
                {
                node          = 1,
                offset        = 1650,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 102
                },
            },
        },

        {
        name    = 'CAB2HL1',
        descr   = 'Аварийная сигнализация. Зеленый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700119',
        DO =
            {
                {
                node          = 2,
                offset        = 596,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 36
                },
            },
        },

        {
        name    = 'CAB2HL2',
        descr   = 'Аварийная сигнализация. Оранжевый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700122',
        DO =
            {
                {
                node          = 2,
                offset        = 597,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 36
                },
            },
        },

        {
        name    = 'CAB2HL3',
        descr   = 'Аварийная сигнализация. Красный',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700115',
        DO =
            {
                {
                node          = 2,
                offset        = 598,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 36
                },
            },
        },

        {
        name    = 'CAB3HL1',
        descr   = 'Аварийная сигнализация. Зеленый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700119',
        DO =
            {
                {
                node          = 3,
                offset        = 1152,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 71
                },
            },
        },

        {
        name    = 'CAB3HL2',
        descr   = 'Аварийная сигнализация. Оранжевый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700122',
        DO =
            {
                {
                node          = 3,
                offset        = 1153,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 71
                },
            },
        },

        {
        name    = 'CAB3HL3',
        descr   = 'Аварийная сигнализация. Красный',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700115',
        DO =
            {
                {
                node          = 3,
                offset        = 1154,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 71
                },
            },
        },

        {
        name    = 'CAB4HL1',
        descr   = 'Аварийная сигнализация. Зеленый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700119',
        DO =
            {
                {
                node          = 4,
                offset        = 1168,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 72
                },
            },
        },

        {
        name    = 'CAB4HL2',
        descr   = 'Аварийная сигнализация. Оранжевый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700122',
        DO =
            {
                {
                node          = 4,
                offset        = 1169,
                physical_port = 31,
                logical_port  = 2,
                module_offset = 72
                },
            },
        },

        {
        name    = 'CAB4HL3',
        descr   = 'Аварийная сигнализация. Красный',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700115',
        DO =
            {
                {
                node          = 4,
                offset        = 1170,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 72
                },
            },
        },

        {
        name    = 'CAB5HL1',
        descr   = 'Аварийная сигнализация. Зеленый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700119',
        DO =
            {
                {
                node          = 5,
                offset        = 1556,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 96
                },
            },
        },

        {
        name    = 'CAB5HL2',
        descr   = 'Аварийная сигнализация. Оранжевый',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700122',
        DO =
            {
                {
                node          = 5,
                offset        = 1557,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 96
                },
            },
        },

        {
        name    = 'CAB5HL3',
        descr   = 'Аварийная сигнализация. Красный',
        dtype   = 11,
        subtype = 1, -- HL
        article = 'PXC.2700115',
        DO =
            {
                {
                node          = 5,
                offset        = 1558,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 96
                },
            },
        },

        {
        name    = 'CAB1SB1',
        descr   = 'Аварийная кнопка. 0=OK',
        dtype   = 12,
        subtype = 1, -- SB
        article = 'XB4BS8445',
        DI =
            {
                {
                node          = 1,
                offset        = 1655,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 102
                },
            },
        },

        {
        name    = 'CAB2SB1',
        descr   = 'Аварийная кнопка. 0=OK',
        dtype   = 12,
        subtype = 1, -- SB
        article = 'XB4BS8445',
        DI =
            {
                {
                node          = 2,
                offset        = 595,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 36
                },
            },
        },

        {
        name    = 'CAB3SB1',
        descr   = 'Аварийная кнопка. 0=OK',
        dtype   = 12,
        subtype = 1, -- SB
        article = 'XB4BS8445',
        DI =
            {
                {
                node          = 3,
                offset        = 1159,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 71
                },
            },
        },

        {
        name    = 'CAB4SB1',
        descr   = 'Аварийная кнопка. 0=OK',
        dtype   = 12,
        subtype = 1, -- SB
        article = 'XB4BS8445',
        DI =
            {
                {
                node          = 4,
                offset        = 1175,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 72
                },
            },
        },

        {
        name    = 'CAB5SB1',
        descr   = 'Аварийная кнопка. 0=OK',
        dtype   = 12,
        subtype = 1, -- SB
        article = 'XB4BS8445',
        DI =
            {
                {
                node          = 5,
                offset        = 2095,
                physical_port = 47,
                logical_port  = 16,
                module_offset = 2080
                },
            },
        },

        {
        name    = 'ALPMAGW5DI1',
        descr   = 'Life bit (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI479001',
        descr   = 'Запрос мойки HWP - 4790 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI479002',
        descr   = 'Возможно включение подающего насоса HWP - 4790 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI479003',
        descr   = 'Объект пустой HWP - 4790 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI479004',
        descr   = 'Устройство безопасности готово (1=OK) HWP - 4790 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1120,
                physical_port = 0,
                logical_port  = 1,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI479011',
        descr   = 'Запрос чистой воды HWP - 4790 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI479012',
        descr   = 'Запрос рассола HWP - 4790 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI479111',
        descr   = 'Запрос чистой воды JWP - 4791 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI480501',
        descr   = 'Запрос мойки BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI480502',
        descr   = 'Возможно включение подающего насоса BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI480503',
        descr   = 'Объект пустой BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI480504',
        descr   = 'Устройство безопасности готово (1=OK) BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1121,
                physical_port = 1,
                logical_port  = 2,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI480510',
        descr   = 'Запрос производства BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI480511',
        descr   = 'Источник сыворотки готов BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482001',
        descr   = 'Запрос мойки WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482002',
        descr   = 'Возможно включение подающего насоса WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482003',
        descr   = 'Объект пустой WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482004',
        descr   = 'Устройство безопасности готово (1=OK) WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1122,
                physical_port = 2,
                logical_port  = 3,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI482010',
        descr   = 'Запрос производства WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482011',
        descr   = 'Запрос открытия входа техног. воды WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482012',
        descr   = 'Запрос открытия выхода техног. воды WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482013',
        descr   = 'Источник сыворотки готов WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI482014',
        descr   = 'Запрос открытия контура нагрева WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI483501',
        descr   = 'Запрос мойки DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI483502',
        descr   = 'Возможно включение подающего насоса DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI483503',
        descr   = 'Объект пустой DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI483504',
        descr   = 'Устройство безопасности готово (1=OK) DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1123,
                physical_port = 3,
                logical_port  = 4,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI483510',
        descr   = 'Запрос производства DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI483511',
        descr   = 'Источник сыворотки готов DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI483514',
        descr   = 'Запрос открытия контура нагрева DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484001',
        descr   = 'Запрос мойки MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484002',
        descr   = 'Возможно включение подающего насоса MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484003',
        descr   = 'Объект пустой MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484004',
        descr   = 'Устройство безопасности готово (1=OK) MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1124,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI484010',
        descr   = 'Запрос производства MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484011',
        descr   = 'Запрос чистой воды MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484012',
        descr   = 'Запрос охлаждающей воды MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484014',
        descr   = 'Запрос открытия контура нагрева MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI484015',
        descr   = 'Запрос опорожнения MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI485001',
        descr   = 'Запрос мойки MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI485002',
        descr   = 'Возможно включение подающего насоса MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI485003',
        descr   = 'Объект пустой MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI485004',
        descr   = 'Устройство безопасности готово (1=OK) MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1125,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI485010',
        descr   = 'Запрос производства MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI485011',
        descr   = 'Запрос чистой воды MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI485014',
        descr   = 'Запрос открытия контура нагрева MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487001',
        descr   = 'Запрос мойки CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487002',
        descr   = 'Возможно включение подающего насоса CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487003',
        descr   = 'Объект пустой CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487004',
        descr   = 'Устройство безопасности готово (1=OK) CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1126,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI487010',
        descr   = 'Запрос производства CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487011',
        descr   = 'Запрос чистой воды CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487012',
        descr   = 'Запрос охлаждающей воды CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487014',
        descr   = 'Запрос опорожнения CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487501',
        descr   = 'Запрос мойки CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487502',
        descr   = 'Возможно включение подающего насоса CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487503',
        descr   = 'Объект пустой CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487504',
        descr   = 'Устройство безопасности готово (1=OK) CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1127,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI487510',
        descr   = 'Запрос производства CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487511',
        descr   = 'Запрос чистой воды CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487512',
        descr   = 'Запрос охлаждающей воды CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI487514',
        descr   = 'Запрос опорожнения CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488501',
        descr   = 'Запрос мойки BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488502',
        descr   = 'Возможно включение подающего насоса BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488503',
        descr   = 'Объект пустой BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488504',
        descr   = 'Устройство безопасности готово (1=OK) BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 1128,
                physical_port = 40,
                logical_port  = 9,
                module_offset = 1120
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'ALPMAGW5DI488506',
        descr   = 'Контура охлаждения 72Y1 открыт BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488507',
        descr   = 'Контура охлаждения 72Y2 открыт BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488510',
        descr   = 'Запрос производства BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488511',
        descr   = 'Запрос чистой воды (рассола) BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488512',
        descr   = 'Запрос охлаждающей воды BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488513',
        descr   = 'Запрос работы с танком рассола BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488514',
        descr   = 'Запрос опорожнения BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DI488516',
        descr   = 'Запрос включения подающего насоса BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'BRN3DI1',
        descr   = 'Запрос мойки (Рассол)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'BRN3DI11',
        descr   = 'Рассол готов (Рассол)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'BRN3DI12',
        descr   = 'Рассол идет (Рассол)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'CAB1DI2',
        descr   = 'Реле безопасности KS1. Выключено. 0=OK',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 1,
                offset        = 1654,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 102
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'CAB2DI2',
        descr   = 'Реле безопасности KS1. Выключено. 0=OK',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 2,
                offset        = 594,
                physical_port = 32,
                logical_port  = 3,
                module_offset = 36
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'CAB3DI2',
        descr   = 'Реле безопасности KS1. Выключено. 0=OK',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 3,
                offset        = 1158,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 71
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'CAB4DI2',
        descr   = 'Реле безопасности KS1. Выключено. 0=OK',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 4,
                offset        = 1174,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 72
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'CAB5DI2',
        descr   = 'Реле безопасности KS1. Выключено. 0=OK',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 5,
                offset        = 2094,
                physical_port = 46,
                logical_port  = 15,
                module_offset = 2080
                },
            },
        par = {1000 --[[P_DT]] }
        },

        {
        name    = 'COAG1DI1',
        descr   = 'Запрос мойки (Сыроизготовитель)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 1,
                offset        = 1107,
                physical_port = 33,
                logical_port  = 4,
                module_offset = 68
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'COAG1DI11',
        descr   = 'Приемник готов (Сыроизготовитель)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 1,
                offset        = 1109,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 68
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'COAG1DI12',
        descr   = 'Запрос нагрева (Сыроизготовитель)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 1,
                offset        = 1110,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 68
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'COAG1DI13',
        descr   = 'Источник сыворотки готов (Сыроизготовитель)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 1,
                offset        = 1111,
                physical_port = 73,
                logical_port  = 8,
                module_offset = 68
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'COAG1DI2',
        descr   = 'Устройство безопасности CIP готово (Сыроизготовитель)',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 1,
                offset        = 1108,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 68
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'MCA4LINE3DI21',
        descr   = 'Линия свободна',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA4LINE3DI22',
        descr   = 'Включение ВН',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA4LINE3DI23',
        descr   = 'Мойка завершена',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI1',
        descr   = 'Линия свободна',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI2',
        descr   = 'Включение ВН',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI3',
        descr   = 'Мойка завершена',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI482001',
        descr   = 'Мойка готова WCSLE-2000 - 4820',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI482002',
        descr   = 'Мойка идет WCSLE-2000 - 4820',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI482003',
        descr   = 'Включение ВН WCSLE-2000 - 4820',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI482004',
        descr   = 'Смена среды WCSLE-2000 - 4820',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI482005',
        descr   = 'Мойка завершена WCSLE-2000 - 4820',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI487501',
        descr   = 'Мойка готова CV-9/2 - 4875',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI487502',
        descr   = 'Мойка идет CV-9/2 - 4875',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI487503',
        descr   = 'Включение ВН CV-9/2 - 4875',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI487504',
        descr   = 'Смена среды CV-9/2 - 4875',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DI487505',
        descr   = 'Мойка завершена CV-9/2 - 4875',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI1',
        descr   = 'Линия свободна',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI2',
        descr   = 'Включение ВН',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI3',
        descr   = 'Мойка завершена',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI484001',
        descr   = 'Мойка готова MC-2000 - 4840',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI484002',
        descr   = 'Мойка идет MC-2000 - 4840',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI484003',
        descr   = 'Включение ВН MC-2000 - 4840',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI484004',
        descr   = 'Смена среды MC-2000 - 4840',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DI484005',
        descr   = 'Мойка завершена MC-2000 - 4840',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI1',
        descr   = 'Линия свободна',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI2',
        descr   = 'Включение ВН',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI3',
        descr   = 'Мойка завершена',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI480501',
        descr   = 'Мойка готова BDC-3000 - 4805',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI480502',
        descr   = 'Мойка идет BDC-3000 - 4805',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI480503',
        descr   = 'Включение ВН BDC-3000 - 4805',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI480504',
        descr   = 'Смена среды BDC-3000 - 4805',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI480505',
        descr   = 'Мойка завершена BDC-3000 - 4805',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI487001',
        descr   = 'Мойка готова CV-5/2 - 4870',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI487002',
        descr   = 'Мойка идет CV-5/2 - 4870',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI487003',
        descr   = 'Включение ВН CV-5/2 - 4870',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI487004',
        descr   = 'Смена среды CV-5/2 - 4870',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI487005',
        descr   = 'Мойка завершена CV-5/2 - 4870',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI488501',
        descr   = 'Мойка готова BV-26/2 - 4885',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI488502',
        descr   = 'Мойка идет BV-26/2 - 4885',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI488503',
        descr   = 'Включение ВН BV-26/2 - 4885',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI488504',
        descr   = 'Смена среды BV-26/2 - 4885',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DI488505',
        descr   = 'Мойка завершена BV-26/2 - 4885',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI1',
        descr   = 'Линия свободна',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI2',
        descr   = 'Включение ВН',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI3',
        descr   = 'Мойка завершена',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI479001',
        descr   = 'Мойка готова HWP - 4790',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI479002',
        descr   = 'Мойка идет HWP - 4790',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI479003',
        descr   = 'Включение ВН HWP - 4790',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI479004',
        descr   = 'Смена среды HWP - 4790',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI479005',
        descr   = 'Мойка завершена HWP - 4790',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI483501',
        descr   = 'Мойка готова DS-1 - 4835',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI483502',
        descr   = 'Мойка идет DS-1 - 4835',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI483503',
        descr   = 'Включение ВН DS-1 - 4835',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI483504',
        descr   = 'Смена среды DS-1 - 4835',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI483505',
        descr   = 'Мойка завершена DS-1 - 4835',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI485001',
        descr   = 'Мойка готова MD4-E - 4850',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI485002',
        descr   = 'Мойка идет MD4-E - 4850',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI485003',
        descr   = 'Включение ВН MD4-E - 4850',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI485004',
        descr   = 'Смена среды MD4-E - 4850',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DI485005',
        descr   = 'Мойка завершена MD4-E - 4850',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'O7DI1',
        descr   = 'Мойка готова (Аппаратный)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'O7DI11',
        descr   = 'Вода в трубе (Аппаратный)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'O7DI12',
        descr   = 'Продукт в трубе (Аппаратный)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'O7DI2',
        descr   = 'Мойка завершена (Аппаратный)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'PFM1DI1',
        descr   = 'Pfm ready washing loader',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 5,
                offset        = 2084,
                physical_port = 4,
                logical_port  = 5,
                module_offset = 2080
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'PFM1DI2',
        descr   = 'Pfm ready washing doser',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 5,
                offset        = 2085,
                physical_port = 5,
                logical_port  = 6,
                module_offset = 2080
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'PFM1DI3',
        descr   = 'Bath water request',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 5,
                offset        = 2086,
                physical_port = 6,
                logical_port  = 7,
                module_offset = 2080
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'PFM1DI4',
        descr   = 'Dosing water request',
        dtype   = 13,
        subtype = 1, -- DI
        article = '',
        DI =
            {
                {
                node          = 5,
                offset        = 2087,
                physical_port = 7,
                logical_port  = 8,
                module_offset = 2080
                },
            },
        par = {500 --[[P_DT]] }
        },

        {
        name    = 'THWP1DI479012',
        descr   = 'Рассол идет (Рассол)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DI1',
        descr   = 'Мойка готова (Ультрафильтрация)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DI11',
        descr   = 'Транзит готов (Ультрафильтрация)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DI12',
        descr   = 'Идет наполнение (Ультрафильтрация)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DI2',
        descr   = 'Пауза (Ультрафильтрация)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'W2DI1',
        descr   = 'Мойка готова (Сыроизготовитель №1+Линия W2) (Сыворотка)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'W2DI11',
        descr   = 'Приемник сыворотки готов (Сыроизготовитель №1) (Сыворотка)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'W2DI480511',
        descr   = 'Приемник сыворотки готов (Сыворотка)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'W2DI482011',
        descr   = 'Приемник сыворотки готов (Сыворотка)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'W2DI483511',
        descr   = 'Приемник сыворотки готов (Сыворотка)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'WLINE5DI1',
        descr   = 'Запрос мойки (Танки воды)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'WLINE5DI11',
        descr   = 'Источник воды готов (Танки воды)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'WLINE5DI12',
        descr   = 'Вода идет (Танки воды)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'WLINE5DI2',
        descr   = 'Мойка завершена (Танки воды)',
        dtype   = 13,
        subtype = 2, -- DI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO1',
        descr   = 'Life bit (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479001',
        descr   = 'Мойка готова HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479002',
        descr   = 'Мойка идет HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479003',
        descr   = 'Включение ВН HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479004',
        descr   = 'Смена среды HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479005',
        descr   = 'Мойка завершена HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479011',
        descr   = 'Чистая вода идет HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479012',
        descr   = 'Рассол идет HWP - 4790 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO479111',
        descr   = 'Чистая вода идет JWP - 4791 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO480501',
        descr   = 'Мойка готова BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO480502',
        descr   = 'Мойка идет BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO480503',
        descr   = 'Включение ВН BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO480504',
        descr   = 'Смена среды BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO480505',
        descr   = 'Мойка завершена BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO480511',
        descr   = 'Приемник сыворотки готов BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482001',
        descr   = 'Мойка готова WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482002',
        descr   = 'Мойка идет WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482003',
        descr   = 'Включение ВН WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482004',
        descr   = 'Смена среды WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482005',
        descr   = 'Мойка завершена WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482011',
        descr   = 'Вход технол. воды открыт WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482012',
        descr   = 'Выход технол. воды открыт WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482013',
        descr   = 'Приемник сыворотки готов WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO482014',
        descr   = 'Контур нагрева открыт WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483501',
        descr   = 'Мойка готова DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483502',
        descr   = 'Мойка идет DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483503',
        descr   = 'Включение ВН DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483504',
        descr   = 'Смена среды DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483505',
        descr   = 'Мойка завершена DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483511',
        descr   = 'Приемник сыворотки готов DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO483514',
        descr   = 'Контур нагрева открыт DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484001',
        descr   = 'Мойка готова MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484002',
        descr   = 'Мойка идет MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484003',
        descr   = 'Включение ВН MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484004',
        descr   = 'Смена среды MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484005',
        descr   = 'Мойка завершена MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484006',
        descr   = 'Промывка контура охлаждения идет MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484011',
        descr   = 'Чистая вода идет MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484012',
        descr   = 'Охлаждающая вода идет MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO484014',
        descr   = 'Контур нагрева открыт MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485001',
        descr   = 'Мойка готова MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485002',
        descr   = 'Мойка идет MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485003',
        descr   = 'Включение ВН MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485004',
        descr   = 'Смена среды MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485005',
        descr   = 'Мойка завершена MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485011',
        descr   = 'Чистая вода идет MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO485014',
        descr   = 'Контур нагрева открыт MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487001',
        descr   = 'Мойка готова CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487002',
        descr   = 'Мойка идет CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487003',
        descr   = 'Включение ВН CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487004',
        descr   = 'Смена среды CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487005',
        descr   = 'Мойка завершена CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487006',
        descr   = 'Промывка контура охлаждения идет CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487010',
        descr   = 'Производство идет CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487011',
        descr   = 'Чистая вода идет CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487012',
        descr   = 'Охлаждающая вода идет CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487014',
        descr   = 'Опорожнение идет CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487501',
        descr   = 'Мойка готова CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487502',
        descr   = 'Мойка идет CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487503',
        descr   = 'Включение ВН CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487504',
        descr   = 'Смена среды CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487505',
        descr   = 'Мойка завершена CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487506',
        descr   = 'Промывка контура охлаждения идет CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487510',
        descr   = 'Производство идет CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487511',
        descr   = 'Чистая вода идет CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487512',
        descr   = 'Охлаждающая вода идет CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO487514',
        descr   = 'Опорожнение идет CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488501',
        descr   = 'Мойка готова BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488502',
        descr   = 'Мойка идет BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488503',
        descr   = 'Включение ВН BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488504',
        descr   = 'Смена среды BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488505',
        descr   = 'Мойка завершена BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488506',
        descr   = 'Промывка контура охлаждения 72Y1 идет BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488507',
        descr   = 'Промывка контура охлаждения 72Y2 идет BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488511',
        descr   = 'Чистая вода (рассол) идет BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488512',
        descr   = 'Охлаждающая вода идет BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488513',
        descr   = 'Танк рассола готов BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5DO488514',
        descr   = 'Опорожнение идет BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'BRN3DO1',
        descr   = 'Мойка готова (Рассол)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'BRN3DO11',
        descr   = 'Приемник рассола готов (Рассол)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'BRN3DO12',
        descr   = 'Запрос рассола (Рассол)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'COAG1DO1',
        descr   = 'Мойка готова (Сыроизготовитель)',
        dtype   = 14,
        subtype = 1, -- DO
        article = '',
        DO =
            {
                {
                node          = 1,
                offset        = 84,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 4
                },
            },
        },

        {
        name    = 'COAG1DO11',
        descr   = 'Источник готов (Сыроизготовитель)',
        dtype   = 14,
        subtype = 1, -- DO
        article = '',
        DO =
            {
                {
                node          = 1,
                offset        = 85,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 4
                },
            },
        },

        {
        name    = 'COAG1DO13',
        descr   = 'Приемник сыворотки готов (Сыроизготовитель)',
        dtype   = 14,
        subtype = 1, -- DO
        article = '',
        DO =
            {
                {
                node          = 1,
                offset        = 86,
                physical_port = 72,
                logical_port  = 7,
                module_offset = 4
                },
            },
        },

        {
        name    = 'MCA4LINE3DO21',
        descr   = 'Готовность объекта CIP Бачок лим.кислоты',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO1',
        descr   = 'Готовность объекта CIP Сыроизготовитель №1+Линия W2',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO482001',
        descr   = 'Готовность объекта CIP WCSLE-2000 - 4820',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO482002',
        descr   = 'Возможно включение подающего насоса WCSLE-2000 - 4820',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO482003',
        descr   = 'Объект пустой WCSLE-2000 - 4820',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO487501',
        descr   = 'Готовность объекта CIP CV-9/2 - 4875',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO487502',
        descr   = 'Возможно включение подающего насоса CV-9/2 - 4875',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO487503',
        descr   = 'Объект пустой CV-9/2 - 4875',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE1DO487504',
        descr   = 'Промывка контура охлаждения идет CV-9/2 - 4875',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DO1',
        descr   = 'Готовность объекта CIP Танк №1 доз-я рассола',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DO2',
        descr   = 'Готовность объекта CIP Танк №2 доз-я рассола',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DO484001',
        descr   = 'Готовность объекта CIP MC-2000 - 4840',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DO484002',
        descr   = 'Возможно включение подающего насоса MC-2000 - 4840',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DO484003',
        descr   = 'Объект пустой MC-2000 - 4840',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE2DO484004',
        descr   = 'Промывка контура охлаждения идет MC-2000 - 4840',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO480501',
        descr   = 'Готовность объекта CIP BDC-3000 - 4805',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO480502',
        descr   = 'Возможно включение подающего насоса BDC-3000 - 4805',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO480503',
        descr   = 'Объект пустой BDC-3000 - 4805',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO487001',
        descr   = 'Готовность объекта CIP CV-5/2 - 4870',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO487002',
        descr   = 'Возможно включение подающего насоса CV-5/2 - 4870',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO487003',
        descr   = 'Объект пустой CV-5/2 - 4870',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO487004',
        descr   = 'Промывка контура охлаждения идет CV-5/2 - 4870',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO488501',
        descr   = 'Готовность объекта CIP BV-26/2 - 4885',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO488502',
        descr   = 'Возможно включение подающего насоса BV-26/2 - 4885',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO488503',
        descr   = 'Объект пустой BV-26/2 - 4885',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE3DO488504',
        descr   = 'Промывка контура охлаждения идет BV-26/2 - 4885',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO1',
        descr   = 'Готовность объекта CIP Резерв',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO2',
        descr   = 'Готовность объекта CIP Резерв',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO3',
        descr   = 'Готовность объекта CIP PFM+транспорт',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO4',
        descr   = 'Готовность объекта CIP Резерв',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO479001',
        descr   = 'Готовность объекта CIP HWP - 4790',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO479002',
        descr   = 'Возможно включение подающего насоса HWP - 4790',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO479003',
        descr   = 'Объект пустой HWP - 4790',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO483501',
        descr   = 'Готовность объекта CIP DS-1 - 4835',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO483502',
        descr   = 'Возможно включение подающего насоса DS-1 - 4835',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO483503',
        descr   = 'Объект пустой DS-1 - 4835',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO485001',
        descr   = 'Готовность объекта CIP MD4-E - 4850',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO485002',
        descr   = 'Возможно включение подающего насоса MD4-E - 4850',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO485003',
        descr   = 'Объект пустой MD4-E - 4850',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO5',
        descr   = 'Готовность объекта CIP Резерв',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'MCA5LINE4DO6',
        descr   = 'Готовность объекта CIP Линия выдачи доз-е рассола',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'O7DO1',
        descr   = 'Запрос мойки (Аппаратный) ',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'O7DO11',
        descr   = 'Приемник готов (Аппаратный)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'O7DO12',
        descr   = 'Запрос проталкивания (Аппаратный)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'O7DO2',
        descr   = 'Пауза (Аппаратный) ',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'PFM1DO1',
        descr   = 'Washing loader start',
        dtype   = 14,
        subtype = 1, -- DO
        article = '',
        DO =
            {
                {
                node          = 5,
                offset        = 532,
                physical_port = 70,
                logical_port  = 5,
                module_offset = 32
                },
            },
        },

        {
        name    = 'PFM1DO2',
        descr   = 'Doser washing starts',
        dtype   = 14,
        subtype = 1, -- DO
        article = '',
        DO =
            {
                {
                node          = 5,
                offset        = 533,
                physical_port = 71,
                logical_port  = 6,
                module_offset = 32
                },
            },
        },

        {
        name    = 'THWP1DO479012',
        descr   = 'Запрос рассола (Рассол)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DO1',
        descr   = 'Запрос мойки (Ультрафильтрация) ',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DO11',
        descr   = 'Запрос транзита (Ультрафильтрация)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'UF1_O7DO2',
        descr   = 'Мойка завершена (Ультрафильтрация) ',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'W2DO1',
        descr   = 'Запрос мойки (Сыроизготовитель №1+Линия W2) (Сыворотка)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'W2DO11',
        descr   = 'Источник сыворотки готов (Сыроизготовитель №1) (Сыворотка)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'W2DO2',
        descr   = 'Мойка завершена (Сыроизготовитель №1+Линия W2) (Сыворотка)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'W2DO480511',
        descr   = 'Источник сыворотки готов (Сыворотка)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'W2DO482011',
        descr   = 'Источник сыворотки готов (Сыворотка)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'W2DO483511',
        descr   = 'Источник сыворотки готов (Сыворотка)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'WLINE5DO1',
        descr   = 'Мойка готова (Танки воды)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'WLINE5DO12',
        descr   = 'Запрос воды (Танки воды)',
        dtype   = 14,
        subtype = 2, -- DO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI480512',
        descr   = 'Состояние насоса BDC-3000 - 4805 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI482012',
        descr   = 'Состояние насоса WCSLE-2000 - 4820 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI483512',
        descr   = 'Состояние насоса DS-1 - 4835 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI484011',
        descr   = 'Задание температуры охлаждения MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI484012',
        descr   = 'Состояние насоса MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI485012',
        descr   = 'Состояние насоса MD4-E - 4850 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI487011',
        descr   = 'Задание температуры охлаждения CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI487012',
        descr   = 'Состояние насоса CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI487511',
        descr   = 'Задание температуры охлаждения CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI487512',
        descr   = 'Состояние насоса CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI488511',
        descr   = 'Задание температуры охлаждения BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI488512',
        descr   = 'Состояние насоса BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AI488513',
        descr   = 'Производительность подающего насоса рассола BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'O7AI11',
        descr   = 'Расход продукта (Аппаратный)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'O7AI12',
        descr   = 'Счетчик продукта (Аппаратный)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'O7AI13',
        descr   = 'Суммарный объем линии (Аппаратный)',
        dtype   = 15,
        subtype = 2, -- AI_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AO484011',
        descr   = 'Температура охлаждающей воды MC-2000 - 4840 (Моцарелла шлюз)',
        dtype   = 16,
        subtype = 2, -- AO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AO487011',
        descr   = 'Температура охлаждающей воды CV-5/2 - 4870 (Моцарелла шлюз)',
        dtype   = 16,
        subtype = 2, -- AO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AO487511',
        descr   = 'Температура охлаждающей воды CV-9/2 - 4875 (Моцарелла шлюз)',
        dtype   = 16,
        subtype = 2, -- AO_VIRT
        article = '',
        },

        {
        name    = 'ALPMAGW5AO488511',
        descr   = 'Температура охлаждающей воды BV-26/2 - 4885 (Моцарелла шлюз)',
        dtype   = 16,
        subtype = 2, -- AO_VIRT
        article = '',
        },

        {
        name    = 'LA_TANK1AO11',
        descr   = 'Текущая концентрация ЛК в смеси (Внутренний сигнал)',
        dtype   = 16,
        subtype = 2, -- AO_VIRT
        article = '',
        },

        {
        name    = 'W2PT1',
        descr   = 'Давление',
        dtype   = 18,
        subtype = 2, -- PT_IOLINK
        article = 'IFM.PM1704',
        AI =
            {
                {
                node          = 1,
                offset        = 71,
                physical_port = 30,
                logical_port  = 1,
                module_offset = 68
                },
            },
        par = {10000 --[[P_ERR]] }
        },

    }

def key_facts(FYEAR,DATE_TO,TABLE):
    keystr = f'''
    DECLARE @NINE INTEGER
    DECLARE @FYEAR  VARCHAR (4)
    DECLARE @END  VARCHAR (10)
    DECLARE @table VARCHAR (15)
    DECLARE @sql NVARCHAR(MAX)

    ----------------------- Update these variables as required --------------------------

    SET @NINE = '8388607'
	--CAST(0x7fffffff AS INT) -- numeric value to be suppressed
    SET @FYEAR = '{FYEAR}'	                 -- represents a financial year, the year selected is the first year of the period e.g. 2012-13 is @FYEAR 2012
	SET @END = '{DATE_TO}'				 -- year and month of the last month for this dateset
	SET @table = '{TABLE}'	         -- processing run with X suffix
    -------------------------------------------------------------------------------------
    SET NOCOUNT ON

    EXEC('
    SELECT * INTO ##proms_processing_KF1a
    FROM
    (
        SELECT 
                    Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,
                ''Provider'' AS [Organisation Type], 
                Q._Q1_PROCODE AS [Organisation Code],
                ''Index'' AS Measure,		
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) 
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,Q._Q1_PROCODE

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''Index'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END)
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,P.ccg_code
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,
            ''England'' AS [Organisation Type], 
            ''England'' AS [Organisation Code],
            ''Index'' AS Measure,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) AS Improved,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) AS Unchanged,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) AS Worsened,
            COUNT(Q.Q2_EQ5D_INDEX) AS TOTAL
            
    FROM proms.QUESTS_'+@table+' Q
    WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
    AND Q._INDEX_CHANGE_FLAG = 1
    AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
    GROUP BY Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE
    
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
            ''Provider'' AS [Organisation Type],   
            Q._Q1_PROCODE AS [Organisation Code],
            ''VAS'' AS Measure,
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
            END AS Improved,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                THEN '+@NINE+'
                ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
            END AS Unchanged,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
            END AS Worsened,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
            END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q._Q1_FYEAR, Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,Q._Q1_PROCODE
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''VAS'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
                END AS Improved,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
                END AS Worsened,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,P.ccg_code

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                ''England'' AS [Organisation Type], 
                ''England'' AS [Organisation Code],
                ''VAS'' AS Measure,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) AS Improved,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) AS Unchanged,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) AS Worsened,
                COUNT(Q.Q2_EQ5D_HEALTH_SCALE) AS TOTAL
            
        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE
            
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                ''Provider'' AS [Organisation Type], 	 
                Q._Q1_PROCODE AS [Organisation Code],
                Q._CS_CODE AS Measure,
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                END AS Improved,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) 
                END AS Worsened,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_CS_SCORE) 
                END AS TOTAL
                        
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE, Q._Q1_PROCODE,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                    ''CCG of GP Practice'' AS [Organisation Type],	
                    P.ccg_code AS [Organisation Code],
                    Q._CS_CODE AS Measure,
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                    END AS Improved,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                    END AS Unchanged,
                    
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR   Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV''THEN ''D'' END) 
                    END AS Worsened,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_CS_SCORE) 
                    END AS TOTAL
                    
        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,P.ccg_code,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,  
                    ''England'' AS [Organisation Type], 
                    ''England'' AS [Organisation Code],
                    Q._CS_CODE AS Measure,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) AS Improved,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) AS Unchanged,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) AS Worsened,

                    COUNT(Q.Q2_CS_SCORE) AS TOTAL
                
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        GROUP BY  Q.PROMS_PROC_CODE,Q._PRIM_REV_PROC_CODE,Q._CS_CODE
    )_


    SELECT * INTO ##proms_processing_KF1b
    FROM
    (
        SELECT 
                    Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 
                Q._Q1_PROCODE AS [Organisation Code],
                ''Index'' AS Measure,		
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) 
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._Q1_PROCODE

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''Index'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END)
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
            ''England'' AS [Organisation Type], 
            ''England'' AS [Organisation Code],
            ''Index'' AS Measure,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) AS Improved,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) AS Unchanged,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) AS Worsened,
            COUNT(Q.Q2_EQ5D_INDEX) AS TOTAL
            
    FROM proms.QUESTS_'+@table+' Q
    WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
    AND Q._INDEX_CHANGE_FLAG = 1
    AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
    GROUP BY Q.PROMS_PROC_CODE
    
    UNION
        SELECT 
                Q.PROMS_PROC_CODE, 
            ''Provider'' AS [Organisation Type],   
            Q._Q1_PROCODE AS [Organisation Code],
            ''VAS'' AS Measure,
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
            END AS Improved,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                THEN '+@NINE+'
                ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
            END AS Unchanged,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
            END AS Worsened,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
            END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q._Q1_FYEAR, Q.PROMS_PROC_CODE,Q._Q1_PROCODE
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''VAS'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
                END AS Improved,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
                END AS Worsened,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE, 
                ''England'' AS [Organisation Type], 
                ''England'' AS [Organisation Code],
                ''VAS'' AS Measure,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) AS Improved,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) AS Unchanged,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) AS Worsened,
                COUNT(Q.Q2_EQ5D_HEALTH_SCALE) AS TOTAL
            
        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q.PROMS_PROC_CODE
            
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 	 
                Q._Q1_PROCODE AS [Organisation Code],
                Q._CS_CODE AS Measure,
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                END AS Improved,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) 
                END AS Worsened,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_CS_SCORE) 
                END AS TOTAL
                        
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE, Q._Q1_PROCODE,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE, 
                    ''CCG of GP Practice'' AS [Organisation Type],	
                    P.ccg_code AS [Organisation Code],
                    Q._CS_CODE AS Measure,
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                    END AS Improved,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                    END AS Unchanged,
                    
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR   Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV''THEN ''D'' END) 
                    END AS Worsened,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_CS_SCORE) 
                    END AS TOTAL
                    
        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,
                    ''England'' AS [Organisation Type], 
                    ''England'' AS [Organisation Code],
                    Q._CS_CODE AS Measure,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) AS Improved,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) AS Unchanged,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) AS Worsened,

                    COUNT(Q.Q2_CS_SCORE) AS TOTAL
                
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        GROUP BY  Q.PROMS_PROC_CODE,Q._CS_CODE
    ) KF1

    SELECT * INTO ##proms_processing_KF2
    FROM
    (
    SELECT
            RP.[Description] AS [Procedure],
            K.[Organisation Type],
            [Organisation Code],
        
            CASE WHEN K.[Organisation Type]= ''England'' THEN ''England''
                WHEN K.[Organisation Type]= ''CCG of GP Practice'' AND K.[Organisation Code]= ''---'' THEN ''Unknown''
                ELSE ISNULL(O.OrgName,''Unknown'')
            END AS [Organsation Name],
        
            RM.[Description] AS [Measure],
            K.[Improved],
            K.[Unchanged],
            K.[Worsened],
            K.[Total],
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Improved] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS IFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Unchanged] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS UFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Worsened] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS WFLAG
        
    FROM ##proms_processing_KF1b K
    LEFT JOIN proms.REF_ORGS_'+@table+' O
    ON o.OrgCode = K.[Organisation Code]
    LEFT JOIN proms.REF_PROCEDURES RP
    ON K.PROMS_PROC_CODE = RP.PROMs_PROC_CODE
    LEFT JOIN proms.REF_MEASURES RM
    ON K.[Measure] = RM.Measure

    union

    SELECT
            RP.[Description] AS [Procedure],
            K.[Organisation Type],
            [Organisation Code],
        
            CASE WHEN K.[Organisation Type]= ''England'' THEN ''England''
                WHEN K.[Organisation Type]= ''CCG of GP Practice'' AND K.[Organisation Code]= ''---'' THEN ''Unknown''
                ELSE ISNULL(O.OrgName,''Unknown'')
            END AS [Organsation Name],
        
            RM.[Description] AS [Measure],
            K.[Improved],
            K.[Unchanged],
            K.[Worsened],
            K.[Total],
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Improved] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS IFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Unchanged] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS UFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Worsened] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS WFLAG
        
    FROM ##proms_processing_KF1a K
    LEFT JOIN proms.REF_ORGS_'+@table+' O
    ON o.OrgCode = K.[Organisation Code]
    LEFT JOIN proms.REF_PROCEDURES RP
    ON K._PRIM_REV_PROC_CODE = RP.PROMs_PROC_CODE
    LEFT JOIN proms.REF_MEASURES RM
    ON K.[Measure] = RM.Measure
    where k._PRIM_REV_PROC_CODE not in (''hr'',''kr'')


    )KF2

    DROP TABLE ##proms_processing_KF1a
    DROP TABLE ##proms_processing_KF1b

    --Contains all the Improved Flags that need secondary suppression
    SELECT * INTO #KFX
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY IFLAG) = 1 
            THEN IFLAG END AS IFLAG
    FROM ##proms_processing_KF2)KFX
    --Contains all the Unchanged Flags that need secondary suppression
    SELECT * INTO #KFY
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY UFLAG) = 1 
            THEN UFLAG END AS UFLAG
    FROM ##proms_processing_KF2)KFY
    --Contains all the Worsened Flags that need secondary suppression
    SELECT * INTO #KFZ
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY WFLAG) = 1 
            THEN WFLAG END AS WFLAG
    FROM ##proms_processing_KF2)KFZ

    SELECT * INTO #KF3
    FROM
    (
        SELECT 
                CASE WHEN KF2.[Organisation Type] = ''England''
                    THEN KF2.[Organisation Type]+KF2.[Organsation Name]+KF2.[Procedure]+KF2.[Measure]
                    ELSE KF2.[Organisation Type]+KF2.[Organsation Name]+'' (''+KF2.[Organisation Code]+'')''+KF2.[Procedure]+KF2.[Measure]
                END AS [Lookup],
                KF2.[Procedure],
                KF2.[Organisation Type],
                KF2.[Organisation Code],
                KF2.[Organsation Name],
                KF2.[Measure],
                KF2.[Improved],
                KF2.[Unchanged],
                KF2.[Worsened],
                KF2.[Total],
                KFX.IFLAG,
                KFY.UFLAG,
                KFZ.WFLAG

        FROM ##proms_processing_KF2 KF2
        LEFT JOIN #KFX KFX
        ON KF2.IFLAG = KFX.IFLAG
        LEFT JOIN #KFY KFY
        ON KF2.UFLAG = KFY.UFLAG
        LEFT JOIN #KFZ KFZ
        ON KF2.WFLAG = KFZ.WFLAG
    )KF3

    DROP TABLE ##proms_processing_KF2
    DROP TABLE #KFX
    DROP TABLE #KFY
    DROP TABLE #KFZ


    --Applies secondary suppression for Provider Improved, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #IFLAG
    FROM
    (
        SELECT
            IFLAG
        FROM #KF3 
        WHERE IFLAG IS NOT NULL
    )KF3A

    --Applies suppression to seleced dataset and joins to main data set
    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            CASE WHEN IFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Improved] END AS [Improved],
            [Unchanged],
            [Worsened],
            CASE WHEN IFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF4
    FROM
    (
        SELECT 
                KF3B.[Lookup],
                KF3B.[Procedure],
                KF3B.[Organisation Type],
                KF3B.[Organisation Code],
                KF3B.[Organsation Name],
                KF3B.[Measure],
                KF3B.[Improved],
                KF3B.[Unchanged],
                KF3B.[Worsened],
                KF3B.[Total],
                KF3A.IFLAG,
                KF3B.UFLAG,
                KF3B.WFLAG,
                ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                    ORDER BY [Total]ASC)AS CLASS
        FROM #KF3 KF3B
        LEFT JOIN #IFLAG KF3A
        ON KF3A.IFLAG = KF3B.[Procedure]+KF3B.Measure
        WHERE KF3B.WFLAG IS NULL
        AND KF3B.[Organisation Type]= ''Provider''
        AND KF3B.Improved > 0
        AND KF3B.Improved < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF3
    WHERE [Lookup] NOT IN
    (
        SELECT 
            KF3B.[Lookup]
            FROM #KF3 KF3B
            LEFT JOIN #IFLAG KF3A
            ON KF3A.IFLAG = KF3B.[Procedure]+KF3B.Measure
            WHERE KF3B.WFLAG IS NULL
            AND KF3B.[Organisation Type]= ''Provider''
            AND KF3B.Improved > 0
            AND KF3B.Improved < '+@NINE+'
    )

    DROP TABLE #KF3
    DROP TABLE #IFLAG


    --SELECT * FROM #KF4
    --DROP TABLE #KF4
    --Applies secondary suppression for Provider Unchanged, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #UFLAG
    FROM
    (
        SELECT
            UFLAG
        FROM #KF4 
        WHERE UFLAG IS NOT NULL
    )KF4A


    --SELECT * FROM #UFLAG
    --Applies suppression to seleced dataset and joins to main data set
    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            CASE WHEN UFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Unchanged] END AS [Unchanged],
            [Worsened],
            CASE WHEN UFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF5
    FROM
    (
        SELECT 
            KF4B.[Lookup],
            KF4B.[Procedure],
            KF4B.[Organisation Type],
            KF4B.[Organisation Code],
            KF4B.[Organsation Name],
            KF4B.[Measure],
            KF4B.[Improved],
            KF4B.[Unchanged],
            KF4B.[Worsened],
            KF4B.[Total],
            KF4B.IFLAG,
            KF4A.UFLAG,
            KF4B.WFLAG,
            ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                ORDER BY [Total]ASC)AS CLASS
        FROM #KF4 KF4B
        LEFT JOIN #UFLAG KF4A
        ON KF4A.UFLAG = KF4B.[Procedure]+KF4B.Measure
        WHERE KF4B.WFLAG IS NULL
        AND KF4B.[Organisation Type]= ''Provider''
        AND KF4B.Unchanged > 0
        AND KF4B.Improved < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF4
    WHERE [Lookup] NOT IN
    (
        SELECT 
            KF4B.[Lookup]
            FROM #KF4 KF4B
            LEFT JOIN #UFLAG KF4A
            ON KF4A.UFLAG = KF4B.[Procedure]+KF4B.Measure
            WHERE KF4B.WFLAG IS NULL
            AND KF4B.[Organisation Type]= ''Provider''
            AND KF4B.Unchanged > 0
            AND KF4B.Unchanged < '+@NINE+'
    )

    DROP TABLE #KF4
    DROP TABLE #UFLAG

    --Applies secondary suppression for Provider Worsened, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #WFLAG
    FROM
    (
    SELECT
        WFLAG
    FROM #KF5 
    WHERE WFLAG IS NOT NULL
    )KF5A

    --Applies suppression to seleced dataset and joins to main data set

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            CASE WHEN WFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Worsened] END AS [Worsened],
            CASE WHEN WFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF6
    FROM
    (
        SELECT 
            KF5B.[Lookup],
            KF5B.[Procedure],
            KF5B.[Organisation Type],
            KF5B.[Organisation Code],
            KF5B.[Organsation Name],
            KF5B.[Measure],
            KF5B.[Improved],
            KF5B.[Unchanged],
            KF5B.[Worsened],
            KF5B.[Total],
            KF5B.IFLAG,
            KF5B.UFLAG,
            KF5A.WFLAG,
            ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                ORDER BY [Total]ASC)AS CLASS
        FROM #KF5 KF5B
        LEFT JOIN #WFLAG KF5A
        ON KF5A.WFLAG = KF5B.[Procedure]+KF5B.Measure
        WHERE KF5B.WFLAG IS NULL
        AND KF5B.[Organisation Type]= ''Provider''
        AND KF5B.Worsened > 0
        AND KF5B.Worsened < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF5
    WHERE [Lookup] NOT IN
    (
    SELECT 
        KF5B.[Lookup]
        FROM #KF5 KF5B
        LEFT JOIN #WFLAG KF5A
        ON KF5A.WFLAG = KF5B.[Procedure]+KF5B.Measure
        WHERE KF5B.WFLAG IS NULL
        AND KF5B.[Organisation Type]= ''Provider''
        AND KF5B.Worsened > 0
        AND KF5B.Worsened < '+@NINE+'
    )

    DROP TABLE #KF5
    DROP TABLE #WFLAG

    SELECT * INTO #KF6a
    FROM
    (
    SELECT	
            ''ENGLANDENGLAND''+[Procedure]+[Measure] AS ''Lookup'',
            CASE WHEN SUM(ENGIFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGIFLAG,
            CASE WHEN SUM(ENGUFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGUFLAG,
            CASE WHEN SUM(ENGWFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGWFLAG,
            CASE WHEN (SUM(ENGIFLAG) = 1 OR SUM(ENGUFLAG) = 1 OR SUM(ENGWFLAG) = 1) THEN '+@NINE+' ELSE 0 END AS ENGTFLAG
    FROM
    (
    SELECT  
            [Procedure],
            [Measure],
            CASE WHEN [Improved] = '+@NINE+' THEN 1 ELSE 0 END AS ENGIFLAG,
            CASE WHEN [Unchanged] = '+@NINE+' THEN 1 ELSE 0 END AS ENGUFLAG,
            CASE WHEN [Worsened] = '+@NINE+' THEN 1 ELSE 0 END AS ENGWFLAG

    FROM #KF6
    WHERE [Organisation Type] = ''Provider''
    )_
    GROUP BY [Procedure],[Measure] 
    )_

    SELECT * INTO #KF6b
    FROM
    (
    SELECT
            KF6.[Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            CASE WHEN ENGIFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Improved] END AS [Improved] ,
            CASE WHEN ENGUFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Unchanged] END AS [Unchanged] ,
            CASE WHEN ENGWFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Worsened] END AS [Worsened] ,
            CASE WHEN ENGTFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Total] END AS [Total]


    FROM #KF6 KF6
    LEFT JOIN #KF6a KF6a
    ON KF6.[Lookup] = KF6a.[Lookup]
    )_
    DROP TABLE #KF6a

    SELECT

        [Lookup],
        [Procedure],
        [Organisation Type],
        [Organisation Code],
        [Organsation Name],
        [Measure],
        [Improved],
        [Unchanged],
        [Worsened],
        [Total],
        CASE WHEN [Improved] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Improved] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Improved],
        
        CASE WHEN [Unchanged] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Unchanged] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Unchanged],
        
        CASE WHEN [Worsened] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Worsened] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Worsened]

    INTO #KF7
    FROM #KF6b

    DROP TABLE #KF6b

    select * into #KF8 from (

    SELECT

        [Lookup],
        [Procedure],
        [Organisation Type],
        [Organisation Code],
        CASE WHEN [Organisation Code] = ''England''
            THEN ''England''
            ELSE [Organsation Name]+'' (''+ [Organisation Code]+'')''
        END AS [Organsation Name],
        [Measure],
        CASE WHEN [Improved] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Improved] AS varchar (10))
        END AS [Improved],
        
        CASE WHEN [Unchanged] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Unchanged] AS varchar (10))
        END AS [Unchanged],
        
        CASE WHEN [Worsened] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Worsened] AS varchar (10))
        END AS [Worsened],
        
        CASE WHEN [Total] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Total] AS varchar (10))
        END AS [Total],
        
        CASE WHEN [% Improved] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Improved] AS varchar (10))+''%''
        END AS [% Improved],
        
        CASE WHEN [% Unchanged] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Unchanged] AS varchar (10))+''%''
        END AS [% Unchanged],
        
        CASE WHEN [% Worsened] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Worsened] AS varchar (10))+''%''
        END AS [% Worsened]
        
    FROM #KF7)_

    DROP TABLE #KF7

    select * into #KF9a1 from #KF8 where [procedure]=''Hip Replacement''
    select * into #KF9a2 from #KF8 where [procedure]=''Hip Replacement Primary''
    select * into #KF9a3 from #KF8 where [procedure]=''Hip Replacement Revision''

    select * into #KF9b1 from #KF8 where [procedure]=''Knee Replacement''
    select * into #KF9b2 from #KF8 where [procedure]=''Knee Replacement Primary''
    select * into #KF9b3 from #KF8 where [procedure]=''Knee Replacement Revision''


    select * into #KF10 from (

    select * from #KF9a1 
    union
    select 
    b.[lookup]
    ,b.[Procedure]
    ,b.[Organisation Type]
    ,b.[Organisation Code]
    ,b.[Organsation Name]
    ,b.[Measure]
    ,case when c.[Improved] = ''*'' then ''*'' else b.[Improved] end as [Improved]
    ,case when c.[Unchanged] = ''*'' then ''*'' else b.[Unchanged] end as [Unchanged]
    ,case when c.[Worsened] = ''*'' then ''*'' else b.[Worsened] end as [Worsened]
    ,case when c.[Total] = ''*'' then ''*'' else b.[Total] end as [Total]
    ,case when c.[% Improved] = ''*'' then ''*'' else b.[% Improved] end as [% Improved]
    ,case when c.[% Unchanged] = ''*'' then ''*'' else b.[% Unchanged] end as [% Unchanged]
    ,case when c.[% Worsened] = ''*'' then ''*'' else b.[% Worsened] end as [% Worsened]

    from #KF9a2 b 
    left join #KF9a3 c on b.[Organisation Code]=c.[Organisation Code] and b.[Measure]=c.[Measure]

    union 
    select * from #KF9a3

    union

    select * from #KF9b1 
    union
    select 
    b.[lookup]
    ,b.[Procedure]
    ,b.[Organisation Type]
    ,b.[Organisation Code]
    ,b.[Organsation Name]
    ,b.[Measure]
    ,case when c.[Improved] = ''*''then ''*''else b.[Improved] end as [Improved]
    ,case when c.[Unchanged] = ''*''then ''*''else b.[Unchanged] end as [Unchanged]
    ,case when c.[Worsened] = ''*''then ''*''else b.[Worsened] end as [Worsened]
    ,case when c.[Total] = ''*''then ''*''else b.[Total] end as [Total]
    ,case when c.[% Improved] = ''*''then ''*''else b.[% Improved] end as [% Improved]
    ,case when c.[% Unchanged] = ''*''then ''*''else b.[% Unchanged] end as [% Unchanged]
    ,case when c.[% Worsened] = ''*''then ''*''else b.[% Worsened] end as [% Worsened]

    from #KF9b2 b 
    left join #KF9b3 c on b.[Organisation Code]=c.[Organisation Code] and b.[Measure]=c.[Measure]

    union 
    select * from #KF9b3)_

    select * from #KF10
    --WHERE [Organsation Name] = ''England''
    ORDER BY
            CASE WHEN [Organsation Name] = ''England'' THEN 1
                ELSE 2
            END ASC,
            [Organisation Type],
            [Procedure],
            Measure


    DROP TABLE #KF6
    DROP TABLE #KF8
    DROP TABLE #KF9a1
    DROP TABLE #KF9a2
    DROP TABLE #KF9a3
    DROP TABLE #KF9b1
    DROP TABLE #KF9b2
    DROP TABLE #KF9b3
    Drop Table #KF10')
    '''
    return keystr

def key_facts_min10(FYEAR,DATE_TO,TABLE):
    keystr = f'''
    DECLARE @NINE INTEGER
    DECLARE @FYEAR  VARCHAR (4)
    DECLARE @END  VARCHAR (10)
    DECLARE @table VARCHAR (15)
    DECLARE @sql NVARCHAR(MAX)

    ----------------------- Update these variables as required --------------------------

    SET @NINE = '8388607'
	--CAST(0x7fffffff AS INT) -- numeric value to be suppressed
    SET @FYEAR = '{FYEAR}'	                 -- represents a financial year, the year selected is the first year of the period e.g. 2012-13 is @FYEAR 2012
	SET @END = '{DATE_TO}'				 -- year and month of the last month for this dateset
	SET @table = '{TABLE}'	         -- processing run with X suffix
    -------------------------------------------------------------------------------------
    SET NOCOUNT ON

    EXEC('
    SELECT * INTO ##proms_processing_KF1a
    FROM
    (
        SELECT 
                    Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 
                Q._Q1_PROCODE AS [Organisation Code],
                ''Index'' AS Measure,		
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) 
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._Q1_PROCODE

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''Index'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END)
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
            ''England'' AS [Organisation Type], 
            ''England'' AS [Organisation Code],
            ''Index'' AS Measure,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) AS Improved,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) AS Unchanged,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) AS Worsened,
            COUNT(Q.Q2_EQ5D_INDEX) AS TOTAL
            
    FROM proms.QUESTS_'+@table+' Q
    WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
    AND Q._INDEX_CHANGE_FLAG = 1
    AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
    GROUP BY Q.PROMS_PROC_CODE,Q.PROMS_PROC_CODE
    
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,  
            ''Provider'' AS [Organisation Type],   
            Q._Q1_PROCODE AS [Organisation Code],
            ''VAS'' AS Measure,
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
            END AS Improved,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                THEN '+@NINE+'
                ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
            END AS Unchanged,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
            END AS Worsened,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
            END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q._Q1_FYEAR, Q.PROMS_PROC_CODE,Q._Q1_PROCODE
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,  
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''VAS'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
                END AS Improved,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
                END AS Worsened,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,  
                ''England'' AS [Organisation Type], 
                ''England'' AS [Organisation Code],
                ''VAS'' AS Measure,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) AS Improved,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) AS Unchanged,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) AS Worsened,
                COUNT(Q.Q2_EQ5D_HEALTH_SCALE) AS TOTAL
            
        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q.PROMS_PROC_CODE,Q.PROMS_PROC_CODE
            
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,  
                ''Provider'' AS [Organisation Type], 	 
                Q._Q1_PROCODE AS [Organisation Code],
                Q._CS_CODE AS Measure,
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                END AS Improved,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) 
                END AS Worsened,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_CS_SCORE) 
                END AS TOTAL
                        
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE, Q._Q1_PROCODE,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,  
                    ''CCG of GP Practice'' AS [Organisation Type],	
                    P.ccg_code AS [Organisation Code],
                    Q._CS_CODE AS Measure,
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                    END AS Improved,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                    END AS Unchanged,
                    
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR   Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV''THEN ''D'' END) 
                    END AS Worsened,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_CS_SCORE) 
                    END AS TOTAL
                    
        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,  
                    ''England'' AS [Organisation Type], 
                    ''England'' AS [Organisation Code],
                    Q._CS_CODE AS Measure,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) AS Improved,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) AS Unchanged,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) AS Worsened,

                    COUNT(Q.Q2_CS_SCORE) AS TOTAL
                
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        GROUP BY  Q.PROMS_PROC_CODE,Q._CS_CODE
    )_


    SELECT * INTO ##proms_processing_KF1b
    FROM
    (
        SELECT 
                    Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 
                Q._Q1_PROCODE AS [Organisation Code],
                ''Index'' AS Measure,		
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) 
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                        AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,Q._Q1_PROCODE

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''Index'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) 
                END AS Improved,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END)
                END AS Unchanged,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) 
                END AS Worsened,
                    
                CASE WHEN COUNT(Q.Q2_EQ5D_INDEX) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_INDEX) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._INDEX_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
            ''England'' AS [Organisation Type], 
            ''England'' AS [Organisation Code],
            ''Index'' AS Measure,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX > Q.Q1_EQ5D_INDEX THEN ''I'' END) AS Improved,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX = Q.Q1_EQ5D_INDEX THEN ''S'' END) AS Unchanged,
            COUNT(CASE WHEN Q.Q2_EQ5D_INDEX < Q.Q1_EQ5D_INDEX THEN ''D'' END) AS Worsened,
            COUNT(Q.Q2_EQ5D_INDEX) AS TOTAL
            
    FROM proms.QUESTS_'+@table+' Q
    WHERE Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
    AND Q._INDEX_CHANGE_FLAG = 1
    AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
    GROUP BY Q.PROMS_PROC_CODE
    
    UNION
        SELECT 
                Q.PROMS_PROC_CODE, 
            ''Provider'' AS [Organisation Type],   
            Q._Q1_PROCODE AS [Organisation Code],
            ''VAS'' AS Measure,
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
            END AS Improved,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                THEN '+@NINE+'
                ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
            END AS Unchanged,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
            END AS Worsened,
                
            CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
            END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q._Q1_FYEAR, Q.PROMS_PROC_CODE,Q._Q1_PROCODE
    
    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE,
                ''CCG of GP Practice'' AS [Organisation Type], 
                P.ccg_code AS [Organisation Code],
                ''VAS'' AS Measure,
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) 
                END AS Improved,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END)BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) 
                END AS Worsened,
                
                CASE WHEN COUNT(Q.Q2_EQ5D_HEALTH_SCALE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_EQ5D_HEALTH_SCALE) 
                END AS TOTAL

        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code

    UNION
    
        SELECT 
                Q.PROMS_PROC_CODE, 
                ''England'' AS [Organisation Type], 
                ''England'' AS [Organisation Code],
                ''VAS'' AS Measure,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE > Q.Q1_EQ5D_HEALTH_SCALE THEN ''I'' END) AS Improved,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE = Q.Q1_EQ5D_HEALTH_SCALE THEN ''S'' END) AS Unchanged,
                COUNT(CASE WHEN Q.Q2_EQ5D_HEALTH_SCALE < Q.Q1_EQ5D_HEALTH_SCALE THEN ''D'' END) AS Worsened,
                COUNT(Q.Q2_EQ5D_HEALTH_SCALE) AS TOTAL
            
        FROM proms.QUESTS_'+@table+' Q
        WHERE  Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCALE_CHANGE_FLAG = 1
        AND Q.PROMS_PROC_CODE in (''hr'',''kr'')
        GROUP BY Q.PROMS_PROC_CODE
            
    UNION
        SELECT 
                Q.PROMS_PROC_CODE,
                ''Provider'' AS [Organisation Type], 	 
                Q._Q1_PROCODE AS [Organisation Code],
                Q._CS_CODE AS Measure,
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                END AS Improved,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                END AS Unchanged,
                
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) 
                END AS Worsened,
                        
                CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                    THEN '+@NINE+'
                    ELSE COUNT(Q.Q2_CS_SCORE) 
                END AS TOTAL
                        
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND Q._Q1_PROCODE IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE, Q._Q1_PROCODE,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE, 
                    ''CCG of GP Practice'' AS [Organisation Type],	
                    P.ccg_code AS [Organisation Code],
                    Q._CS_CODE AS Measure,
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) 
                    END AS Improved,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) 
                    END AS Unchanged,
                    
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        AND  COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                        OR   Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV''THEN ''D'' END) 
                    END AS Worsened,
                            
                    CASE WHEN COUNT(Q.Q2_CS_SCORE) BETWEEN 1 AND 5 
                        THEN '+@NINE+'
                        ELSE COUNT(Q.Q2_CS_SCORE) 
                    END AS TOTAL
                    
        FROM proms.QUESTS_'+@table+' Q
        LEFT JOIN proms.HES_PROCEDURES_'+@table+' P
        ON Q._P_REF_PROM = P._P_REF_PROM
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        AND P.ccg_code IS NOT NULL
        GROUP BY  Q.PROMS_PROC_CODE,P.ccg_code,Q._CS_CODE
        
    UNION
    
        SELECT 
                    Q.PROMS_PROC_CODE,
                    ''England'' AS [Organisation Type], 
                    ''England'' AS [Organisation Code],
                    Q._CS_CODE AS Measure,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''I'' END) AS Improved,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE = Q.Q1_CS_SCORE THEN ''S'' END) AS Unchanged,

                    COUNT(CASE WHEN Q.Q2_CS_SCORE < Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE IN (''KR'',''HR'') 
                    OR Q.Q2_CS_SCORE > Q.Q1_CS_SCORE AND Q.PROMS_PROC_CODE = ''VV'' THEN ''D'' END) AS Worsened,

                    COUNT(Q.Q2_CS_SCORE) AS TOTAL
                
        FROM proms.QUESTS_'+@table+' Q
        WHERE Q.PROMS_PROC_CODE IN (''hr'',''kr'')
        AND Q._Q1_FYEAR = \'\'\'+@FYEAR+\'\'\'
        AND Q._Q1_YEAR_MONTH <= \'\'\'+@END+\'\'\'
        AND Q._SCORE_CHANGE_FLAG = 1
        GROUP BY  Q.PROMS_PROC_CODE,Q._CS_CODE
    ) KF1

    SELECT * INTO ##proms_processing_KF2
    FROM
    (
    SELECT
            RP.[Description] AS [Procedure],
            K.[Organisation Type],
            [Organisation Code],
        
            CASE WHEN K.[Organisation Type]= ''England'' THEN ''England''
                WHEN K.[Organisation Type]= ''CCG of GP Practice'' AND K.[Organisation Code]= ''---'' THEN ''Unknown''
                ELSE ISNULL(O.OrgName,''Unknown'')
            END AS [Organsation Name],
        
            RM.[Description] AS [Measure],
            K.[Improved],
            K.[Unchanged],
            K.[Worsened],
            K.[Total],
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Improved] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS IFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Unchanged] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS UFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Worsened] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS WFLAG
        
    FROM ##proms_processing_KF1b K
    LEFT JOIN proms.REF_ORGS_'+@table+' O
    ON o.OrgCode = K.[Organisation Code]
    LEFT JOIN proms.REF_PROCEDURES RP
    ON K.PROMS_PROC_CODE = RP.PROMs_PROC_CODE
    LEFT JOIN proms.REF_MEASURES RM
    ON K.[Measure] = RM.Measure

    union

    SELECT
            RP.[Description] AS [Procedure],
            K.[Organisation Type],
            [Organisation Code],
        
            CASE WHEN K.[Organisation Type]= ''England'' THEN ''England''
                WHEN K.[Organisation Type]= ''CCG of GP Practice'' AND K.[Organisation Code]= ''---'' THEN ''Unknown''
                ELSE ISNULL(O.OrgName,''Unknown'')
            END AS [Organsation Name],
        
            RM.[Description] AS [Measure],
            K.[Improved],
            K.[Unchanged],
            K.[Worsened],
            K.[Total],
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Improved] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS IFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Unchanged] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS UFLAG,
            CASE WHEN K.[Organisation Type] = ''Provider'' AND K.[Worsened] = '+@NINE+' THEN RP.[Description]+RM.[Description] END AS WFLAG
        
    FROM ##proms_processing_KF1a K
    LEFT JOIN proms.REF_ORGS_'+@table+' O
    ON o.OrgCode = K.[Organisation Code]
    LEFT JOIN proms.REF_PROCEDURES RP
    ON K.PROMS_PROC_CODE = RP.PROMs_PROC_CODE
    LEFT JOIN proms.REF_MEASURES RM
    ON K.[Measure] = RM.Measure
    where k.PROMS_PROC_CODE not in (''hr'',''kr'')


    )KF2

    DROP TABLE ##proms_processing_KF1a
    DROP TABLE ##proms_processing_KF1b

    --Contains all the Improved Flags that need secondary suppression
    SELECT * INTO #KFX
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY IFLAG) = 1 
            THEN IFLAG END AS IFLAG
    FROM ##proms_processing_KF2)KFX
    --Contains all the Unchanged Flags that need secondary suppression
    SELECT * INTO #KFY
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY UFLAG) = 1 
            THEN UFLAG END AS UFLAG
    FROM ##proms_processing_KF2)KFY
    --Contains all the Worsened Flags that need secondary suppression
    SELECT * INTO #KFZ
    FROM
    (
    SELECT
        CASE WHEN COUNT('+@NINE+') OVER (PARTITION BY WFLAG) = 1 
            THEN WFLAG END AS WFLAG
    FROM ##proms_processing_KF2)KFZ

    SELECT * INTO #KF3
    FROM
    (
        SELECT 
                CASE WHEN KF2.[Organisation Type] = ''England''
                    THEN KF2.[Organisation Type]+KF2.[Organsation Name]+KF2.[Procedure]+KF2.[Measure]
                    ELSE KF2.[Organisation Type]+KF2.[Organsation Name]+'' (''+KF2.[Organisation Code]+'')''+KF2.[Procedure]+KF2.[Measure]
                END AS [Lookup],
                KF2.[Procedure],
                KF2.[Organisation Type],
                KF2.[Organisation Code],
                KF2.[Organsation Name],
                KF2.[Measure],
                KF2.[Improved],
                KF2.[Unchanged],
                KF2.[Worsened],
                KF2.[Total],
                KFX.IFLAG,
                KFY.UFLAG,
                KFZ.WFLAG

        FROM ##proms_processing_KF2 KF2
        LEFT JOIN #KFX KFX
        ON KF2.IFLAG = KFX.IFLAG
        LEFT JOIN #KFY KFY
        ON KF2.UFLAG = KFY.UFLAG
        LEFT JOIN #KFZ KFZ
        ON KF2.WFLAG = KFZ.WFLAG
    )KF3

    DROP TABLE ##proms_processing_KF2
    DROP TABLE #KFX
    DROP TABLE #KFY
    DROP TABLE #KFZ


    --Applies secondary suppression for Provider Improved, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #IFLAG
    FROM
    (
        SELECT
            IFLAG
        FROM #KF3 
        WHERE IFLAG IS NOT NULL
    )KF3A

    --Applies suppression to seleced dataset and joins to main data set
    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            CASE WHEN IFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Improved] END AS [Improved],
            [Unchanged],
            [Worsened],
            CASE WHEN IFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF4
    FROM
    (
        SELECT 
                KF3B.[Lookup],
                KF3B.[Procedure],
                KF3B.[Organisation Type],
                KF3B.[Organisation Code],
                KF3B.[Organsation Name],
                KF3B.[Measure],
                KF3B.[Improved],
                KF3B.[Unchanged],
                KF3B.[Worsened],
                KF3B.[Total],
                KF3A.IFLAG,
                KF3B.UFLAG,
                KF3B.WFLAG,
                ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                    ORDER BY [Total]ASC)AS CLASS
        FROM #KF3 KF3B
        LEFT JOIN #IFLAG KF3A
        ON KF3A.IFLAG = KF3B.[Procedure]+KF3B.Measure
        WHERE KF3B.WFLAG IS NULL
        AND KF3B.[Organisation Type]= ''Provider''
        AND KF3B.Improved > 0
        AND KF3B.Improved < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF3
    WHERE [Lookup] NOT IN
    (
        SELECT 
            KF3B.[Lookup]
            FROM #KF3 KF3B
            LEFT JOIN #IFLAG KF3A
            ON KF3A.IFLAG = KF3B.[Procedure]+KF3B.Measure
            WHERE KF3B.WFLAG IS NULL
            AND KF3B.[Organisation Type]= ''Provider''
            AND KF3B.Improved > 0
            AND KF3B.Improved < '+@NINE+'
    )

    DROP TABLE #KF3
    DROP TABLE #IFLAG


    --SELECT * FROM #KF4
    --DROP TABLE #KF4
    --Applies secondary suppression for Provider Unchanged, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #UFLAG
    FROM
    (
        SELECT
            UFLAG
        FROM #KF4 
        WHERE UFLAG IS NOT NULL
    )KF4A


    --SELECT * FROM #UFLAG
    --Applies suppression to seleced dataset and joins to main data set
    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            CASE WHEN UFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Unchanged] END AS [Unchanged],
            [Worsened],
            CASE WHEN UFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF5
    FROM
    (
        SELECT 
            KF4B.[Lookup],
            KF4B.[Procedure],
            KF4B.[Organisation Type],
            KF4B.[Organisation Code],
            KF4B.[Organsation Name],
            KF4B.[Measure],
            KF4B.[Improved],
            KF4B.[Unchanged],
            KF4B.[Worsened],
            KF4B.[Total],
            KF4B.IFLAG,
            KF4A.UFLAG,
            KF4B.WFLAG,
            ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                ORDER BY [Total]ASC)AS CLASS
        FROM #KF4 KF4B
        LEFT JOIN #UFLAG KF4A
        ON KF4A.UFLAG = KF4B.[Procedure]+KF4B.Measure
        WHERE KF4B.WFLAG IS NULL
        AND KF4B.[Organisation Type]= ''Provider''
        AND KF4B.Unchanged > 0
        AND KF4B.Improved < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF4
    WHERE [Lookup] NOT IN
    (
        SELECT 
            KF4B.[Lookup]
            FROM #KF4 KF4B
            LEFT JOIN #UFLAG KF4A
            ON KF4A.UFLAG = KF4B.[Procedure]+KF4B.Measure
            WHERE KF4B.WFLAG IS NULL
            AND KF4B.[Organisation Type]= ''Provider''
            AND KF4B.Unchanged > 0
            AND KF4B.Unchanged < '+@NINE+'
    )

    DROP TABLE #KF4
    DROP TABLE #UFLAG

    --Applies secondary suppression for Provider Worsened, if needed
    --Identifies Procedures and Measures to be supressed

    SELECT * INTO #WFLAG
    FROM
    (
    SELECT
        WFLAG
    FROM #KF5 
    WHERE WFLAG IS NOT NULL
    )KF5A

    --Applies suppression to seleced dataset and joins to main data set

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            CASE WHEN WFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Worsened] END AS [Worsened],
            CASE WHEN WFLAG IS NOT NULL AND CLASS = 1 THEN '+@NINE+' ELSE [Total] END AS [Total],
            IFLAG,
            UFLAG,
            WFLAG
    INTO #KF6
    FROM
    (
        SELECT 
            KF5B.[Lookup],
            KF5B.[Procedure],
            KF5B.[Organisation Type],
            KF5B.[Organisation Code],
            KF5B.[Organsation Name],
            KF5B.[Measure],
            KF5B.[Improved],
            KF5B.[Unchanged],
            KF5B.[Worsened],
            KF5B.[Total],
            KF5B.IFLAG,
            KF5B.UFLAG,
            KF5A.WFLAG,
            ROW_NUMBER()OVER(PARTITION BY [Procedure], [Measure]
                                ORDER BY [Total]ASC)AS CLASS
        FROM #KF5 KF5B
        LEFT JOIN #WFLAG KF5A
        ON KF5A.WFLAG = KF5B.[Procedure]+KF5B.Measure
        WHERE KF5B.WFLAG IS NULL
        AND KF5B.[Organisation Type]= ''Provider''
        AND KF5B.Worsened > 0
        AND KF5B.Worsened < '+@NINE+'
    )_

    UNION

    SELECT 
            [Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            [Improved],
            [Unchanged],
            [Worsened],
            [Total],
            IFLAG,
            UFLAG,
            WFLAG 
    FROM #KF5
    WHERE [Lookup] NOT IN
    (
    SELECT 
        KF5B.[Lookup]
        FROM #KF5 KF5B
        LEFT JOIN #WFLAG KF5A
        ON KF5A.WFLAG = KF5B.[Procedure]+KF5B.Measure
        WHERE KF5B.WFLAG IS NULL
        AND KF5B.[Organisation Type]= ''Provider''
        AND KF5B.Worsened > 0
        AND KF5B.Worsened < '+@NINE+'
    )

    DROP TABLE #KF5
    DROP TABLE #WFLAG

    SELECT * INTO #KF6a
    FROM
    (
    SELECT	
            ''ENGLANDENGLAND''+[Procedure]+[Measure] AS ''Lookup'',
            CASE WHEN SUM(ENGIFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGIFLAG,
            CASE WHEN SUM(ENGUFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGUFLAG,
            CASE WHEN SUM(ENGWFLAG) = 1 THEN '+@NINE+' ELSE 0 END AS ENGWFLAG,
            CASE WHEN (SUM(ENGIFLAG) = 1 OR SUM(ENGUFLAG) = 1 OR SUM(ENGWFLAG) = 1) THEN '+@NINE+' ELSE 0 END AS ENGTFLAG
    FROM
    (
    SELECT  
            [Procedure],
            [Measure],
            CASE WHEN [Improved] = '+@NINE+' THEN 1 ELSE 0 END AS ENGIFLAG,
            CASE WHEN [Unchanged] = '+@NINE+' THEN 1 ELSE 0 END AS ENGUFLAG,
            CASE WHEN [Worsened] = '+@NINE+' THEN 1 ELSE 0 END AS ENGWFLAG

    FROM #KF6
    WHERE [Organisation Type] = ''Provider''
    )_
    GROUP BY [Procedure],[Measure] 
    )_

    SELECT * INTO #KF6b
    FROM
    (
    SELECT
            KF6.[Lookup],
            [Procedure],
            [Organisation Type],
            [Organisation Code],
            [Organsation Name],
            [Measure],
            CASE WHEN ENGIFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Improved] END AS [Improved] ,
            CASE WHEN ENGUFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Unchanged] END AS [Unchanged] ,
            CASE WHEN ENGWFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Worsened] END AS [Worsened] ,
            CASE WHEN ENGTFLAG = '+@NINE+' THEN '+@NINE+' ELSE [Total] END AS [Total]


    FROM #KF6 KF6
    LEFT JOIN #KF6a KF6a
    ON KF6.[Lookup] = KF6a.[Lookup]
    )_
    DROP TABLE #KF6a

    SELECT

        [Lookup],
        [Procedure],
        [Organisation Type],
        [Organisation Code],
        [Organsation Name],
        [Measure],
        [Improved],
        [Unchanged],
        [Worsened],
        [Total],
        CASE WHEN [Improved] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Improved] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Improved],
        
        CASE WHEN [Unchanged] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Unchanged] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Unchanged],
        
        CASE WHEN [Worsened] = '+@NINE+' OR [Total] = '+@NINE+'
            THEN '+@NINE+'
            ELSE CAST(CAST([Worsened] AS DECIMAL (10,1))/CAST([Total] AS DECIMAL (10,1))*100 AS DECIMAL (10,1))
        END AS [% Worsened]

    INTO #KF7
    FROM #KF6b

    DROP TABLE #KF6b

    select * into #KF8 from (

    SELECT

        [Lookup],
        [Procedure],
        [Organisation Type],
        [Organisation Code],
        CASE WHEN [Organisation Code] = ''England''
            THEN ''England''
            ELSE [Organsation Name]+'' (''+ [Organisation Code]+'')''
        END AS [Organsation Name],
        [Measure],
        CASE WHEN [Improved] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Improved] AS varchar (10))
        END AS [Improved],
        
        CASE WHEN [Unchanged] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Unchanged] AS varchar (10))
        END AS [Unchanged],
        
        CASE WHEN [Worsened] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Worsened] AS varchar (10))
        END AS [Worsened],
        
        CASE WHEN [Total] = '+@NINE+'
            THEN ''*''
            ELSE CAST([Total] AS varchar (10))
        END AS [Total],
        
        CASE WHEN [% Improved] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Improved] AS varchar (10))+''%''
        END AS [% Improved],
        
        CASE WHEN [% Unchanged] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Unchanged] AS varchar (10))+''%''
        END AS [% Unchanged],
        
        CASE WHEN [% Worsened] = '+@NINE+'
            THEN ''*''
            ELSE CAST([% Worsened] AS varchar (10))+''%''
        END AS [% Worsened]
        
    FROM #KF7)_

    DROP TABLE #KF7

    select * into #KF9a1 from #KF8 where [procedure]=''Hip Replacement''
    select * into #KF9a2 from #KF8 where [procedure]=''Hip Replacement Primary''
    select * into #KF9a3 from #KF8 where [procedure]=''Hip Replacement Revision''

    select * into #KF9b1 from #KF8 where [procedure]=''Knee Replacement''
    select * into #KF9b2 from #KF8 where [procedure]=''Knee Replacement Primary''
    select * into #KF9b3 from #KF8 where [procedure]=''Knee Replacement Revision''


    select * into #KF10 from (

    select * from #KF9a1 
    union
    select 
    b.[lookup]
    ,b.[Procedure]
    ,b.[Organisation Type]
    ,b.[Organisation Code]
    ,b.[Organsation Name]
    ,b.[Measure]
    ,case when c.[Improved] = ''*'' then ''*'' else b.[Improved] end as [Improved]
    ,case when c.[Unchanged] = ''*'' then ''*'' else b.[Unchanged] end as [Unchanged]
    ,case when c.[Worsened] = ''*'' then ''*'' else b.[Worsened] end as [Worsened]
    ,case when c.[Total] = ''*'' then ''*'' else b.[Total] end as [Total]
    ,case when c.[% Improved] = ''*'' then ''*'' else b.[% Improved] end as [% Improved]
    ,case when c.[% Unchanged] = ''*'' then ''*'' else b.[% Unchanged] end as [% Unchanged]
    ,case when c.[% Worsened] = ''*'' then ''*'' else b.[% Worsened] end as [% Worsened]

    from #KF9a2 b 
    left join #KF9a3 c on b.[Organisation Code]=c.[Organisation Code] and b.[Measure]=c.[Measure]

    union 
    select * from #KF9a3

    union

    select * from #KF9b1 
    union
    select 
    b.[lookup]
    ,b.[Procedure]
    ,b.[Organisation Type]
    ,b.[Organisation Code]
    ,b.[Organsation Name]
    ,b.[Measure]
    ,case when c.[Improved] = ''*''then ''*''else b.[Improved] end as [Improved]
    ,case when c.[Unchanged] = ''*''then ''*''else b.[Unchanged] end as [Unchanged]
    ,case when c.[Worsened] = ''*''then ''*''else b.[Worsened] end as [Worsened]
    ,case when c.[Total] = ''*''then ''*''else b.[Total] end as [Total]
    ,case when c.[% Improved] = ''*''then ''*''else b.[% Improved] end as [% Improved]
    ,case when c.[% Unchanged] = ''*''then ''*''else b.[% Unchanged] end as [% Unchanged]
    ,case when c.[% Worsened] = ''*''then ''*''else b.[% Worsened] end as [% Worsened]

    from #KF9b2 b 
    left join #KF9b3 c on b.[Organisation Code]=c.[Organisation Code] and b.[Measure]=c.[Measure]

    union 
    select * from #KF9b3)_

    select * from #KF10
    --WHERE [Organsation Name] = ''England''
    ORDER BY
            CASE WHEN [Organsation Name] = ''England'' THEN 1
                ELSE 2
            END ASC,
            [Organisation Type],
            [Procedure],
            Measure


    DROP TABLE #KF6
    DROP TABLE #KF8
    DROP TABLE #KF9a1
    DROP TABLE #KF9a2
    DROP TABLE #KF9a3
    DROP TABLE #KF9b1
    DROP TABLE #KF9b2
    DROP TABLE #KF9b3
    Drop Table #KF10')
    '''
    return keystr

def successatisf(YEAR_STRING,TABLE,DATE_FROM,DATE_TO):

    successatisf_str=f'''

        SET NOCOUNT ON

        EXEC('

        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'',

        ''Success'' AS ''Breakdown'', Q2_SUCCESS AS Sort,

        case when Q2_SUCCESS = 1 then ''Much Better''

            when Q2_SUCCESS = 2 then ''Little Better''

            when Q2_SUCCESS = 3 then ''About the Same''

            when Q2_SUCCESS = 4 THEN ''Little Worse''

            when Q2_SUCCESS = 5 THEN ''Much Worse''

            else '' ''

        END AS ''Answer'', 

        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''

        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}

        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and 

        PROMS_PROC_CODE=''HR'' AND Q2_SUCCESS IN (1,2,3,4,5)

        group by Q2_SUCCESS


        union


        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'',

        ''Success'' AS ''Breakdown'', Q2_SUCCESS AS Sort,

        case when Q2_SUCCESS = 1 then ''Much Better''

            when Q2_SUCCESS = 2 then ''Little Better''

            when Q2_SUCCESS = 3 then ''About the Same''

            when Q2_SUCCESS = 4 THEN ''Little Worse''

            when Q2_SUCCESS = 5 THEN ''Much Worse''

            else '' ''

        END AS ''Answer'', 

        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''

        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}

        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and 

        PROMS_PROC_CODE=''KR'' AND Q2_SUCCESS IN (1,2,3,4,5)

        group by Q2_SUCCESS


        union


        /*** Satisfaction ***/

        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Hip Replacement'' AS ''Procedure'',

        ''Satisfaction'' AS ''Breakdown'', Q2_SATISFACTION AS Sort, 

        case when Q2_SATISFACTION = 1 then ''Excellent''

            when Q2_SATISFACTION = 2 then ''Very Good''

            when Q2_SATISFACTION = 3 then ''Good''

            when Q2_SATISFACTION = 4 THEN ''Fair''

            when Q2_SATISFACTION = 5 THEN ''Poor''

            else '' ''

        END AS ''Answer'',

        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''

        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}

        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and 

        PROMS_PROC_CODE=''HR'' AND Q2_SATISFACTION IN (1,2,3,4,5)

        group by Q2_SATISFACTION


        union


        select ''{YEAR_STRING}'' AS ''Financial Year'', ''Knee Replacement'' AS ''Procedure'',

        ''Satisfaction'' AS ''Breakdown'', Q2_SATISFACTION AS Sort, 

        case when Q2_SATISFACTION = 1 then ''Excellent''

            when Q2_SATISFACTION = 2 then ''Very Good''

            when Q2_SATISFACTION = 3 then ''Good''

            when Q2_SATISFACTION = 4 THEN ''Fair''

            when Q2_SATISFACTION = 5 THEN ''Poor''

            else '' ''

        END AS ''Answer'',

        count(*) * 100.0 / sum(count(*)) over() AS ''Percentage''

        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}

        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' 

        and PROMS_PROC_CODE=''KR'' AND Q2_SATISFACTION IN (1,2,3,4,5)

        group by Q2_SATISFACTION')

    '''


    return successatisf_str

def patient_profile(PROCEDURE,TABLE,DATE_FROM,DATE_TO):
    patient_profile_query=f'''
    SET NOCOUNT ON 
    EXEC('
        SELECT _AGE_GROUP_5YR, SUM(CASE  WHEN _AGE_GROUP_5YR=''85+'' THEN Female ELSE Female END) As''Female'',
        SUM(CASE  WHEN _AGE_GROUP_5YR=''85+'' THEN Male ELSE Male END) AS ''Male''
        FROM (
        select CASE WHEN A._AGE_GROUP_5YR IN (''85 to 89'',''90 to 120'') THEN ''85+''
        ELSE A._AGE_GROUP_5YR
        END AS _AGE_GROUP_5YR,Female,Male
        from (SELECT _AGE_GROUP_5YR, count (*) AS ''Female'' FROM PROMS_PUBLICATION.proms.HES_PROCEDURES_{TABLE}
        where EPISTART between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROCEDURE}''
        AND _AGE_GROUP_5YR IS NOT NULL AND SEX=''2''
        group by _AGE_GROUP_5YR) A
        JOIN (select _AGE_GROUP_5YR, count (*) AS ''Male''
        from PROMS_PUBLICATION.proms.HES_PROCEDURES_{TABLE}
        where EPISTART between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROCEDURE}''
        AND _AGE_GROUP_5YR IS NOT NULL AND SEX=''1''
        group by _AGE_GROUP_5YR) B
        ON A._AGE_GROUP_5YR=B._AGE_GROUP_5YR
        ) C
        GROUP BY _AGE_GROUP_5YR')'''
    return patient_profile_query

def quarters(DATE_TO,DATE_FROM,TABLE):
    quarters_str = f'''
    SET NOCOUNT ON
    EXEC ('
        if OBJECT_ID(''tempdb..#Q1_EQ5D'') is not null
        drop table #Q1_EQ5D

        select Q1_EQ5D_INDEX
        into #Q1_EQ5D
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR'' 
        AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null

        if OBJECT_ID(''tempdb..#Q2_EQ5D'') is not null
        drop table #Q2_EQ5D

        select Q2_EQ5D_INDEX
        into #Q2_EQ5D
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR'' 
        AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null

        if OBJECT_ID(''tempdb..#Q1_EQ5DKR'') is not null
        drop table #Q1_EQ5DKR

        select Q1_EQ5D_INDEX
        into #Q1_EQ5DKR
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR'' 
        AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null

        if OBJECT_ID(''tempdb..#Q2_EQ5DKR'') is not null
        drop table #Q2_EQ5DKR

        select Q2_EQ5D_INDEX
        into #Q2_EQ5DKR
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR'' 
        AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null

        /**Oxford Score**/
        if OBJECT_ID(''tempdb..#Q1_OHS'') is not null
        drop table #Q1_OHS

        select Q1_CS_SCORE
        into #Q1_OHS
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR'' 
        AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null

        if OBJECT_ID(''tempdb..#Q2_OHS'') is not null
        drop table #Q2_OHS

        select Q2_CS_SCORE
        into #Q2_OHS
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR'' 
        AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null

        if OBJECT_ID(''tempdb..#Q1_OHSKR'') is not null
        drop table #Q1_OHSKR

        select Q1_CS_SCORE
        into #Q1_OHSKR
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR'' 
        AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null

        if OBJECT_ID(''tempdb..#Q2_OHSKR'') is not null
        drop table #Q2_OHSKR

        select Q2_CS_SCORE
        into #Q2_OHSKR
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR'' 
        AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null

        /** EQ VAS **/
        if OBJECT_ID(''tempdb..#Q1_EQVAS'') is not null
        drop table #Q1_EQVAS

        select Q1_EQ5D_HEALTH_SCALE*1.0 AS Q1_EQ5D_HEALTH_SCALE
        into #Q1_EQVAS
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR'' AND 
            Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 and Q2_EQ5D_HEALTH_SCALE is not null 
            and Q2_EQ5D_HEALTH_SCALE<>999

        if OBJECT_ID(''tempdb..#Q2_EQVAS'') is not null
        drop table #Q2_EQVAS

        select Q2_EQ5D_HEALTH_SCALE*1.0 AS Q2_EQ5D_HEALTH_SCALE
        into #Q2_EQVAS
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''HR'' AND 
            Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 and Q2_EQ5D_HEALTH_SCALE is not null 
            and Q2_EQ5D_HEALTH_SCALE<>999

        if OBJECT_ID(''tempdb..#Q1_EQVASKR'') is not null
        drop table #Q1_EQVASKR

        select Q1_EQ5D_HEALTH_SCALE*1.0 AS Q1_EQ5D_HEALTH_SCALE
        into #Q1_EQVASKR
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR'' AND 
            Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 and Q2_EQ5D_HEALTH_SCALE is not null 
            and Q2_EQ5D_HEALTH_SCALE<>999

        if OBJECT_ID(''tempdb..#Q2_EQVASKR'') is not null
        drop table #Q2_EQVASKR

        select Q2_EQ5D_HEALTH_SCALE*1.0 AS Q2_EQ5D_HEALTH_SCALE
        into #Q2_EQVASKR
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''KR'' AND 
            Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 and Q2_EQ5D_HEALTH_SCALE is not null 
            and Q2_EQ5D_HEALTH_SCALE<>999

        /** Final Table creation **/
        /**EQ5D**/
        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ5D'' AS ''Measure'', ''HR'' AS ''Proc'', ''Pre-op'' AS Questionnaire, 
		(SELECT DISTINCT first_value(Q1_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q1_EQ5D_INDEX) p FROM #Q1_EQ5D) t) AS Q1,
		(SELECT DISTINCT first_value(Q1_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q1_EQ5D_INDEX) p FROM #Q1_EQ5D) t) AS Median,
		(SELECT DISTINCT first_value(Q1_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q1_EQ5D_INDEX) p FROM #Q1_EQ5D) t) AS Q3
        from #Q1_EQ5D ) A,(

        SELECT TOP 1
        avg(Q1_EQ5D_INDEX) as ''Mean''
        from #Q1_EQ5D) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ5D'' AS ''Measure'', ''HR'' AS ''Proc'', ''Post-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q2_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q2_EQ5D_INDEX) p FROM #Q2_EQ5D) t) AS Q1,
		(SELECT DISTINCT first_value(Q2_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q2_EQ5D_INDEX) p FROM #Q2_EQ5D) t) AS Median,
		(SELECT DISTINCT first_value(Q2_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q2_EQ5D_INDEX) p FROM #Q2_EQ5D) t) AS Q3

        from #Q2_EQ5D ) A,(

        SELECT TOP 1
        avg(Q2_EQ5D_INDEX) as ''Mean''
        from #Q2_EQ5D) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ5D'' AS ''Measure'', ''KR'' AS ''Proc'', ''Pre-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q1_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q1_EQ5D_INDEX) p FROM #Q1_EQ5DKR) t) AS Q1,
		(SELECT DISTINCT first_value(Q1_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q1_EQ5D_INDEX) p FROM #Q1_EQ5DKR) t) AS Median,
		(SELECT DISTINCT first_value(Q1_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q1_EQ5D_INDEX) p FROM #Q1_EQ5DKR) t) AS Q3

        from #Q1_EQ5DKR ) A,(

        SELECT TOP 1
        avg(Q1_EQ5D_INDEX) as ''Mean''
        from #Q1_EQ5DKR) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ5D'' AS ''Measure'', ''KR'' AS ''Proc'', ''Post-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q2_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q2_EQ5D_INDEX) p FROM #Q2_EQ5DKR) t) AS Q1,
		(SELECT DISTINCT first_value(Q2_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q2_EQ5D_INDEX) p FROM #Q2_EQ5DKR) t) AS Median,
		(SELECT DISTINCT first_value(Q2_EQ5D_INDEX) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_INDEX, percent_rank() OVER (ORDER BY Q2_EQ5D_INDEX) p FROM #Q2_EQ5DKR) t) AS Q3
        from #Q2_EQ5DKR ) A,(

        SELECT TOP 1
        avg(Q2_EQ5D_INDEX) as ''Mean''
        from #Q2_EQ5DKR) B

        /** oxford score **/

        union 

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''Oxford Score'' AS ''Measure'', ''HR'' AS ''Proc'', ''Pre-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q1_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q1_CS_SCORE, percent_rank() OVER (ORDER BY Q1_CS_SCORE) p FROM #Q1_OHS) t) AS Q1,
		(SELECT DISTINCT first_value(Q1_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q1_CS_SCORE, percent_rank() OVER (ORDER BY Q1_CS_SCORE) p FROM #Q1_OHS) t) AS Median,
		(SELECT DISTINCT first_value(Q1_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q1_CS_SCORE, percent_rank() OVER (ORDER BY Q1_CS_SCORE) p FROM #Q1_OHS) t) AS Q3

        from #Q1_OHS ) A,(

        SELECT TOP 1
        avg(Q1_CS_SCORE) as ''Mean''
        from #Q1_OHS) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''Oxford Score'' AS ''Measure'', ''HR'' AS ''Proc'', ''Post-op'' AS Questionnaire, 
       (SELECT DISTINCT first_value(Q2_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q2_CS_SCORE, percent_rank() OVER (ORDER BY Q2_CS_SCORE) p FROM #Q1_OHS) t) AS Q1,
		(SELECT DISTINCT first_value(Q2_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q2_CS_SCORE, percent_rank() OVER (ORDER BY Q2_CS_SCORE) p FROM #Q1_OHS) t) AS Median,
		(SELECT DISTINCT first_value(Q2_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q2_CS_SCORE, percent_rank() OVER (ORDER BY Q2_CS_SCORE) p FROM #Q1_OHS) t) AS Q3

        from #Q2_OHS ) A,(

        SELECT TOP 1
        avg(Q2_CS_SCORE) as ''Mean''
        from #Q2_OHS) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''Oxford Score'' AS ''Measure'', ''KR'' AS ''Proc'', ''Pre-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q1_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q1_CS_SCORE, percent_rank() OVER (ORDER BY Q1_CS_SCORE) p FROM #Q1_OHSKR) t) AS Q1,
		(SELECT DISTINCT first_value(Q1_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q1_CS_SCORE, percent_rank() OVER (ORDER BY Q1_CS_SCORE) p FROM #Q1_OHSKR) t) AS Median,
		(SELECT DISTINCT first_value(Q1_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q1_CS_SCORE, percent_rank() OVER (ORDER BY Q1_CS_SCORE) p FROM #Q1_OHSKR) t) AS Q3

        from #Q1_OHSKR ) A,(

        SELECT TOP 1
        avg(Q1_CS_SCORE) as ''Mean''
        from #Q1_OHSKR) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''Oxford Score'' AS ''Measure'', ''KR'' AS ''Proc'', ''Post-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q2_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q2_CS_SCORE, percent_rank() OVER (ORDER BY Q2_CS_SCORE) p FROM #Q2_OHSKR) t) AS Q1,
		(SELECT DISTINCT first_value(Q2_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q2_CS_SCORE, percent_rank() OVER (ORDER BY Q2_CS_SCORE) p FROM #Q2_OHSKR) t) AS Median,
		(SELECT DISTINCT first_value(Q2_CS_SCORE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q2_CS_SCORE, percent_rank() OVER (ORDER BY Q2_CS_SCORE) p FROM #Q2_OHSKR) t) AS Q3

        from #Q2_OHSKR ) A,(

        SELECT TOP 1
        avg(Q2_CS_SCORE) as ''Mean''
        from #Q2_OHSKR) B

        /** EQ VAS**/

        union 

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ VAS'' AS ''Measure'', ''HR'' AS ''Proc'', ''Pre-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q1_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q1_EQ5D_HEALTH_SCALE) p FROM #Q1_EQVAS) t) AS Q1,
		(SELECT DISTINCT first_value(Q1_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q1_EQ5D_HEALTH_SCALE) p FROM #Q1_EQVAS) t) AS Median,
		(SELECT DISTINCT first_value(Q1_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q1_EQ5D_HEALTH_SCALE) p FROM #Q1_EQVAS) t) AS Q3

        from #Q1_EQVAS ) A,(

        SELECT TOP 1
        avg(Q1_EQ5D_HEALTH_SCALE) as ''Mean''
        from #Q1_EQVAS) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ VAS'' AS ''Measure'', ''HR'' AS ''Proc'', ''Post-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q2_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q2_EQ5D_HEALTH_SCALE) p FROM #Q2_EQVAS) t) AS Q1,
		(SELECT DISTINCT first_value(Q2_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q2_EQ5D_HEALTH_SCALE) p FROM #Q2_EQVAS) t) AS Median,
		(SELECT DISTINCT first_value(Q2_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q2_EQ5D_HEALTH_SCALE) p FROM #Q2_EQVAS) t) AS Q3

        from #Q2_EQVAS ) A,(

        SELECT TOP 1
        avg(Q2_EQ5D_HEALTH_SCALE) as ''Mean''
        from #Q2_EQVAS) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ VAS'' AS ''Measure'', ''KR'' AS ''Proc'', ''Pre-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q1_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q1_EQ5D_HEALTH_SCALE) p FROM #Q1_EQVASKR) t) AS Q1,
		(SELECT DISTINCT first_value(Q1_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q1_EQ5D_HEALTH_SCALE) p FROM #Q1_EQVASKR) t) AS Median,
		(SELECT DISTINCT first_value(Q1_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q1_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q1_EQ5D_HEALTH_SCALE) p FROM #Q1_EQVASKR) t) AS Q3

        from #Q1_EQVASKR ) A,(

        SELECT TOP 1
        avg(Q1_EQ5D_HEALTH_SCALE) as ''Mean''
        from #Q1_EQVASKR) B

        union

        SELECT Measure,[Proc],Questionnaire, Mean, Q1,Median,Q3 
        FROM (
        SELECT TOP 1 ''EQ VAS'' AS ''Measure'', ''KR'' AS ''Proc'', ''Post-op'' AS Questionnaire, 
        (SELECT DISTINCT first_value(Q2_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.25 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q2_EQ5D_HEALTH_SCALE) p FROM #Q2_EQVASKR) t) AS Q1,
		(SELECT DISTINCT first_value(Q2_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.5 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q2_EQ5D_HEALTH_SCALE) p FROM #Q2_EQVASKR) t) AS Median,
		(SELECT DISTINCT first_value(Q2_EQ5D_HEALTH_SCALE) OVER (ORDER BY CASE WHEN p <= 0.75 THEN p END DESC) Q1
		FROM (SELECT Q2_EQ5D_HEALTH_SCALE, percent_rank() OVER (ORDER BY Q2_EQ5D_HEALTH_SCALE) p FROM #Q2_EQVASKR) t) AS Q3

        from #Q2_EQVASKR ) A,(

        SELECT TOP 1
        avg(Q2_EQ5D_HEALTH_SCALE) as ''Mean''
        from #Q2_EQVASKR) B
    ')
    '''
    return quarters_str

def max_scores(DATE_FROM,DATE_TO,TABLE,PROC):
    max_scores_string = f'''
    SET NOCOUNT ON

    EXEC('
    declare @PROC_NUM_CS FLOAT
    declare @PROC_NUM_EQVAS FLOAT
    DECLARE @PROC_NUM_EQ5D FLOAT

    SET @PROC_NUM_CS = (SELECT count (*)
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null);

    SET @PROC_NUM_EQVAS = (select count (*)
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}''and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 
    and Q2_EQ5D_HEALTH_SCALE is not null and Q2_EQ5D_HEALTH_SCALE<>999)

    SET @PROC_NUM_EQ5D = (select count (*)
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null)


    select ''Oxford Score'' AS ''Measure'', @PROC_NUM_CS AS ''Number'',1 AS ''Percentage''

    union all 

    select ''Pre op scores at max value CS'' AS ''Measure'', count (*) AS ''Number'', ROUND( count(*)/@PROC_NUM_CS,3) AS ''Percentage''
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
        and Q1_CS_SCORE=48

    union all

    select ''Pre and post scores at max value CS'' AS ''Measure'', count (*) AS ''Number'', ROUND( count(*)/@PROC_NUM_CS,3) AS ''Percentage''
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
        and Q1_CS_SCORE=48 and Q2_CS_SCORE=48

    union all 

    select ''EQ 5D Index'' AS ''Measure'', @PROC_NUM_EQ5D AS ''Number'',1 AS ''Percentage''

    union all 

    select ''Pre op scores at max value EQ5D'' AS ''Measure'', count (*) AS ''Number'', ROUND( count(*)/@PROC_NUM_EQ5D,3) AS ''Percentage''
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null
        and Q1_EQ5D_INDEX=1 

    union all

    select ''Pre and post scores at max value EQ5D'' AS ''Measure'', count (*) AS ''Number'', ROUND(count(*)/@PROC_NUM_EQ5D,3) AS ''Percentage''
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_EQ5D_INDEX is not null and Q2_EQ5D_INDEX is not null
        and Q1_EQ5D_INDEX=1 and Q2_EQ5D_INDEX=1

        union all 

    select ''EQ VAS'' AS ''Measure'', @PROC_NUM_EQVAS AS ''Number'',1 AS ''Percentage''

    union all 

    select ''Pre op scores at max value EQVAS'' AS ''Measure'', count (*) AS ''Number'', ROUND( count(*)/ @PROC_NUM_EQVAS,3) AS ''Percentage''
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 
        and Q2_EQ5D_HEALTH_SCALE is not null and Q2_EQ5D_HEALTH_SCALE<>999 and Q1_EQ5D_HEALTH_SCALE=100

    union all

    select ''Pre and post scores at max value EQVAS'' AS ''Measure'', count (*) AS ''Number'', ROUND( count(*)/ @PROC_NUM_EQVAS,3) AS ''Percentage''
    from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
    where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}'' AND Q1_EQ5D_HEALTH_SCALE is not null AND Q1_EQ5D_HEALTH_SCALE<>999 
        and Q2_EQ5D_HEALTH_SCALE is not null and Q2_EQ5D_HEALTH_SCALE<>999 and Q1_EQ5D_HEALTH_SCALE=100 and Q2_EQ5D_HEALTH_SCALE=100
        ')
    '''
    return max_scores_string

def complications(TABLE,DATE_FROM,DATE_TO,PROC):
    complications_str = f'''
        SET NOCOUNT ON
        EXEC('
        /** At least 1 **/
        select ''At_Least_1'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and (Q2_ALLERGY=1 or Q2_BLEEDING=1 or Q2_WOUND=1 or Q2_URINE=1)

        union all
        /** Allergy **/
        select ''Allergy'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and Q2_ALLERGY=1

        union all
        /** Bleeding **/
        select ''Bleeding'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and Q2_BLEEDING=1

        union all
        /** Urinary **/
        select ''Urinary'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and Q2_URINE=1



        union all
        /** Wound **/
        select ''Wound'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and Q2_WOUND=1 


        union all
        /** Readmitted **/
        select ''Readmitted'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and Q2_READMITTED=1

        union all
        /** Further surgery **/
        select ''Further_Surgery'' as ''Symptom'', count (*) AS ''Number''
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}'' and PROMS_PROC_CODE=''{PROC}''
            and Q2_FURTHER_SURGERY=1
            ')
    '''
    return complications_str 

def q2_returned(DATE_FROM,DATE_TO,TABLE,PROC):
    q2s_returned = f'''
    SET ARITHABORT OFF 
    SET ANSI_WARNINGS OFF
    SET NOCOUNT ON
    
    EXEC('
    SELECT COUNT(_Q2_SENT_FLAG)
    from  proms.QUESTS_{TABLE}
    WHERE _Q2_SENT_FLAG=1 AND _Q1_PROXY_DATE between ''{DATE_FROM}'' and ''{DATE_TO}''
    AND PROMS_PROC_CODE = ''{PROC}'' AND _Q2_RETURNED_FLAG = 1')
    '''
    return q2s_returned

def patient_engagement(DATE_FROM,DATE_TO,TABLE,FYEAR):
    add_year_patient_engagement = f'''
        SET NOCOUNT ON
        INSERT INTO PROMS_DEVELOPMENT.proms.past10yearsEngagement SELECT * FROM (
        SELECT A.Year,A.EpisodesHR,B.Q1_RETURNED_HR,B.Q2_RETURNED_HR, C.EpisodesKR,D.Q1_Returned_KR,D.Q2_Returned_KR
        FROM (SELECT {FYEAR} AS 'Year',COUNT(EPIKEY) as 'EpisodesHR'
        from PROMS_PUBLICATION.proms.HES_PROCEDURES_{TABLE}
        where EPISTART between '{DATE_FROM}' and '{DATE_TO}' 
        and PROMS_PROC_CODE = 'HR') as A, 
        (SELECT {FYEAR} AS 'Year',COUNT(_Q1_PROXY_DATE) AS 'Q1_Returned_HR', SUM(CASE WHEN _Q2_RETURNED_FLAG=1 THEN 1 ELSE 0 END) AS 'Q2_Returned_HR'
        FROM PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' 
        and PROMS_PROC_CODE = 'HR') AS B,
        (SELECT {FYEAR} AS 'Year',COUNT(EPIKEY) as 'EpisodesKR'
        from PROMS_PUBLICATION.proms.HES_PROCEDURES_{TABLE}
        where EPISTART between '{DATE_FROM}' and '{DATE_TO}' 
        and PROMS_PROC_CODE = 'KR') as C,
        (SELECT {FYEAR} AS 'Year',COUNT(_Q1_PROXY_DATE) AS 'Q1_Returned_KR', SUM(CASE WHEN _Q2_RETURNED_FLAG=1 THEN 1 ELSE 0 END) AS 'Q2_Returned_KR'
        FROM PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' 
        and PROMS_PROC_CODE = 'KR') AS D) AS E;'''
   
    return add_year_patient_engagement

def patient_engagement_data(FYEAR):
     patient_engagement_data = f'''
        SELECT DISTINCT * 
        FROM PROMS_DEVELOPMENT.proms.past10yearsEngagement
        WHERE Year between {str(int(FYEAR)-9)} and {FYEAR};
    '''
     return patient_engagement_data
def severe_scores_hr(TABLE,DATE_FROM,DATE_TO):
    most_severe_hr = f'''
        DECLARE @denominator FLOAT

        SET @denominator = (select count (*)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null);


        Select b.Measure, [Pre-op],[Post-Op]
        FROM (
        select *
        from (

        /*** WALKING ***/
        select '1. Walking' as 'Measure', ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_WALKING in (0,1)

        union
        /*** STAIRS ***/
        select '2. Stairs' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_STAIRS in (0,1)

        union
        /*** SHOPPING ***/
        select '3. Shopping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_SHOPPING in (0,1)

        union
        /*** DRESSING ***/
        select '4. Dressing' as 'Measure', ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_DRESSING in (0,1)

        union
        /*** TRANSPORT ***/
        select '5. Transport' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_TRANSPORT in (0,1)

        union
        /*** WASHING ***/
        select '6. Washing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_WASHING in (0,1)

        union
        /*** WORK ***/
        select '7. Work' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_WORK in (0,1)

        union
        /*** LIMPING ***/
        select '8. Limping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_LIMPING in (0,1)

        union
        /*** SUDDEN PAIN ***/
        select '9. Sudden pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_SUDDEN_PAIN in (0,1)

        union
        /*** NIGHT PAIN ***/
        select '10. Night pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_NIGHT_PAIN in (0,1)

        union
        /*** PAIN ***/
        select '11. Pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_PAIN in (0,1)

        union
        /*** STANDING ***/
        select '12. Standing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q1_STANDING in (0,1)
        )a

        )b

        JOIN (
        select *
        from (

        /*** WALKING ***/
        select '1. Walking' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_WALKING in (0,1)

        union
        /*** STAIRS ***/
        select '2. Stairs' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_STAIRS in (0,1)

        union
        /*** SHOPPING ***/
        select '3. Shopping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_SHOPPING in (0,1)

        union
        /*** DRESSING ***/
        select '4. Dressing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_DRESSING in (0,1)

        union
        /*** TRANSPORT ***/
        select '5. Transport' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_TRANSPORT in (0,1)

        union
        /*** WASHING ***/
        select '6. Washing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_WASHING in (0,1)

        union
        /*** WORK ***/
        select '7. Work' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_WORK in (0,1)

        union
        /*** LIMPING ***/
        select '8. Limping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_LIMPING in (0,1)

        union
        /*** SUDDEN PAIN ***/
        select '9. Sudden pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_SUDDEN_PAIN in (0,1)

        union
        /*** NIGHT PAIN ***/
        select '10. Night pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_NIGHT_PAIN in (0,1)

        union
        /*** PAIN ***/
        select '11. Pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_PAIN in (0,1)

        union
        /*** STANDING ***/
        select '12. Standing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='HR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and HR_Q2_STANDING in (0,1)
        )c
        )d ON b.Measure = d.Measure;
        '''
    return most_severe_hr

def severe_scores_kr(TABLE,DATE_FROM,DATE_TO):
    most_severe_kr = f'''
        DECLARE @denominator FLOAT

        SET @denominator = (select count (*)
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null);


        Select b.Measure, [Pre-op],[Post-Op]
        FROM (
        select *
        from (

        /*** WALKING ***/
        select '1. Walking' as 'Measure', ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_WALKING in (0,1)

        union
        /*** STAIRS ***/
        select '2. Stairs' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_STAIRS in (0,1)

        union
        /*** SHOPPING ***/
        select '3. Shopping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_SHOPPING in (0,1)

        union
        /*** DRESSING ***/
        select '4. Kneeling' as 'Measure', ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_KNEELING in (0,1)

        union
        /*** TRANSPORT ***/
        select '5. Transport' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_TRANSPORT in (0,1)

        union
        /*** WASHING ***/
        select '6. Washing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_WASHING in (0,1)

        union
        /*** GIVE WAY ***/
        select '7. Give Way' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_CONFIDENCE in (0,1)


        union
        /*** WORK ***/
        select '8. Work' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_WORK in (0,1)

        union
        /*** LIMPING ***/
        select '9. Limping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_LIMPING in (0,1)

        union
        /*** NIGHT PAIN ***/
        select '10. Night pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_NIGHT_PAIN in (0,1)

        union
        /*** PAIN ***/
        select '11. Pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_PAIN in (0,1)

        union
        /*** STANDING ***/
        select '12. Standing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Pre-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q1_STANDING in (0,1)
        )a

        )b

        JOIN (
        select *
        from (

        /*** WALKING ***/
        select '1. Walking' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_WALKING in (0,1)

        union
        /*** STAIRS ***/
        select '2. Stairs' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_STAIRS in (0,1)

        union
        /*** SHOPPING ***/
        select '3. Shopping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_SHOPPING in (0,1)

        union
        /*** DRESSING ***/
        select '4. Kneeling' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_KNEELING in (0,1)

        union
        /*** TRANSPORT ***/
        select '5. Transport' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_TRANSPORT in (0,1)

        union
        /*** WASHING ***/
        select '6. Washing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_WASHING in (0,1)

        union
        /*** GIVE WAY ***/
        select '7. Give Way' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_CONFIDENCE in (0,1)

        union
        /*** WORK ***/
        select '8. Work' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_WORK in (0,1)

        union
        /*** LIMPING ***/
        select '9. Limping' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_LIMPING in (0,1)

        union
        /*** NIGHT PAIN ***/
        select '10. Night pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_NIGHT_PAIN in (0,1)

        union
        /*** PAIN ***/
        select '11. Pain' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_PAIN in (0,1)

        union
        /*** STANDING ***/
        select '12. Standing' as 'Measure',  ROUND(count (*)/@denominator,3) as 'Post-Op'
        from PROMS_PUBLICATION.proms.QUESTS_{TABLE}
        where _Q1_PROXY_DATE between '{DATE_FROM}' and '{DATE_TO}' and PROMS_PROC_CODE='KR' and Q1_CS_SCORE is not null and Q2_CS_SCORE is not null
            and KR_Q2_STANDING in (0,1)
        )c
        )d ON b.Measure = d.Measure;
    '''
    return most_severe_kr

def ons_data(FYEAR):
    ons_data_query = f'''
        SELECT CASE WHEN AGE_LOWER BETWEEN 10 AND 14 THEN '10 to 14'
        WHEN AGE_LOWER BETWEEN 15 AND 19 THEN '15 to 19'
        WHEN AGE_LOWER BETWEEN 20 AND 24 THEN '20 to 24'
        WHEN AGE_LOWER BETWEEN 25 and 29 then '25 to 29'
        WHEN AGE_LOWER BETWEEN 30 and 34 then '30 to 34'
        when AGE_LOWER between 35 and 39 then '35 to 39'
        when AGE_LOWER between 40 and 44 then '40 to 44'
        when AGE_LOWER between 45 and 49 then '45 to 49'
        when AGE_LOWER between 50 and 54 then '50 to 54'
        when AGE_LOWER between 55 and 59 then '55 to 59'
        when AGE_LOWER between 60 and 64 then '60 to 64'
        when AGE_LOWER between 65 and 69 then '65 to 69'
        when AGE_LOWER between 70 and 74 then '70 to 74'
        when AGE_LOWER between 75 and 79 then '75 to 79'
        when AGE_LOWER between 80 and 84 then '80 to 84'
        when AGE_LOWER>84 then '85+'
        Else NULL 
        END AS AgeBand, GENDER, SUM(POPULATION_COUNT) AS Count
        FROM [PROMS_HES].[dbo].[ONS_POPULATION_V2]
        WHERE YEAR_OF_COUNT = {FYEAR} AND GEOGRAPHIC_GROUP_CODE = 'E92' AND AGE_LOWER>=10
        GROUP BY (CASE WHEN AGE_LOWER BETWEEN 10 AND 14 THEN '10 to 14'
        WHEN AGE_LOWER BETWEEN 15 AND 19 THEN '15 to 19'
        WHEN AGE_LOWER BETWEEN 20 AND 24 THEN '20 to 24'
        WHEN AGE_LOWER BETWEEN 25 and 29 then '25 to 29'
        WHEN AGE_LOWER BETWEEN 30 and 34 then '30 to 34'
        when AGE_LOWER between 35 and 39 then '35 to 39'
        when AGE_LOWER between 40 and 44 then '40 to 44'
        when AGE_LOWER between 45 and 49 then '45 to 49'
        when AGE_LOWER between 50 and 54 then '50 to 54'
        when AGE_LOWER between 55 and 59 then '55 to 59'
        when AGE_LOWER between 60 and 64 then '60 to 64'
        when AGE_LOWER between 65 and 69 then '65 to 69'
        when AGE_LOWER between 70 and 74 then '70 to 74'
        when AGE_LOWER between 75 and 79 then '75 to 79'
        when AGE_LOWER between 80 and 84 then '80 to 84'
        when AGE_LOWER>84 then '85+'
        Else NULL 
        END),GENDER
    '''
    return ons_data_query


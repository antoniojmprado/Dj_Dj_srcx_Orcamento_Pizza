 with `base_diaria` as
 (
	select  `f`.`maquina_id` AS `maq_fin_id`,
			`f`.`custo_minuto` AS `custo_minuto`,
			`maq`.`id` AS `maquinaId`,
			`maq`.`nome` AS `maquina`,
			sum(`ht`.`qt_horas_turno` * `td`.`qt_turnos_dia`) * 60 AS `minutos_planejados`,
            sum(`oc`.`tempo_parado`/60000000) as `tempo_parado_min`,
            avg(`oc`.`performance`) AS `performance`,
			avg(`oc`.`qualidade`) AS `qualidade` 
				from  `appoee_ocorrencia` `oc` 
					join `maquina` `maq` on `maq`.`id` = `oc`.`maquina_id`  
					join `horas_turno` `ht` on `ht`.`id` = `oc`.`horas_turno_id`
					join `turnos_dia` `td` on `td`.`id` = `oc`.`turnos_dia_id`   
					join `appoee_maquinafinancas` `f` on `f`.`maquina_id` = `oc`.`maquina_id`
    group by `maq`.`id`,`maq`.`nome`
    ) 
		select
        `base_diaria`.`maquina` AS `maquina`,
        `base_diaria`.`tempo_parado_min`,
        `base_diaria`.`maquinaId` AS `maquinaId`,`base_diaria`.`custo_minuto` AS 
        `custo_minuto`,`base_diaria`.`minutos_planejados` AS `minutos_planejados`,
        `base_diaria`.`tempo_parado_min` * `base_diaria`.`custo_minuto` AS `prejuizo_perda_tempo`,
        (`base_diaria`.`minutos_planejados` - `base_diaria`.`minutos_planejados` * `base_diaria`.`performance` / 100) *`base_diaria`.`custo_minuto` AS `prejuizo_perda_performance`,
        (`base_diaria`.`minutos_planejados` - `base_diaria`.`minutos_planejados` *`base_diaria`.`qualidade` / 100) * `base_diaria`.`custo_minuto` AS `prejuizo_perda_qualidade` 
from `base_diaria`
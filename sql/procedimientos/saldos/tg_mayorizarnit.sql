-- DROP FUNCTION public.tg_mayorizarnit();

CREATE OR REPLACE FUNCTION public.tg_mayorizarnit()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
Declare lnidDoc int = new.documento_id
       ;lnidestado int = CASE WHEN COALESCE(new.sistema, 0) = 2 THEN 2 ELSE 1 END
	   ;lnidmayor int = new.mayor_id
	   ;lnidpersona int = new.persona_id
	   ;lnmes int
	   ;lnaño int
	   ;lncontsaldo int
	   ;lnvalor_db decimal(18,2) = COALESCE(new.valor_db,0.00)
	   ;lnvalor_cr decimal(18,2) = COALESCE(new.valor_cr,0.00)
	   ;lcsql  VARCHAR(10485760)
	   ;lcPar varchar(10485760)
	   ;lncnit int
	   ;lnidTabla int
	   ;lnsali decimal(18,2)=0.00
	   ;lnd01 decimal(18,2) = 0.00
	   ;lnh01 decimal(18,2) = 0.00
	   ;lnsal01 decimal(18,2) = 0.00
	   ;lnd02 decimal(18,2) = 0.00
	   ;lnh02 decimal(18,2) = 0.00
	   ;lnsal02 decimal(18,2) = 0.00
	   ;lnd03 decimal(18,2) = 0.00
	   ;lnh03 decimal(18,2) = 0.00
	   ;lnsal03 decimal(18,2) = 0.00
	   ;lnd04 decimal(18,2) = 0.00
	   ;lnh04 decimal(18,2) = 0.00
	   ;lnsal04 decimal(18,2) = 0.00
	   ;lnd05 decimal(18,2) = 0.00
	   ;lnh05 decimal(18,2) = 0.00
	   ;lnsal05 decimal(18,2) = 0.00
	   ;lnd06 decimal(18,2) = 0.00
	   ;lnh06 decimal(18,2) = 0.00
	   ;lnsal06 decimal(18,2) = 0.00
	   ;lnd07 decimal(18,2) = 0.00
	   ;lnh07 decimal(18,2) = 0.00
	   ;lnsal07 decimal(18,2) = 0.00
	   ;lnd08 decimal(18,2) = 0.00
	   ;lnh08 decimal(18,2) = 0.00
	   ;lnsal08 decimal(18,2) = 0.00
	   ;lnd09 decimal(18,2) = 0.00
	   ;lnh09 decimal(18,2) = 0.00
	   ;lnsal09 decimal(18,2) = 0.00
	   ;lnd10 decimal(18,2) = 0.00
	   ;lnh10 decimal(18,2) = 0.00
	   ;lnsal10 decimal(18,2) = 0.00
	   ;lnd11 decimal(18,2) = 0.00
	   ;lnh11 decimal(18,2) = 0.00
	   ;lnsal11 decimal(18,2) = 0.00
	   ;lnd12 decimal(18,2) = 0.00
	   ;lnh12 decimal(18,2) = 0.00
	   ;lnsal12 decimal(18,2) = 0.00
	   ;lnd13 decimal(18,2) = 0.00
	   ;lnh13 decimal(18,2) = 0.00
	   ;lnsal13 decimal(18,2) = 0.00
	   ;lndcierre integer = COALESCE(new.dcierre,0);
BEGIN
	if lnidpersona is null then
		return NULL;
	end if;

	select  extract(month from ab.fecha), extract(year from ab.fecha) into lnmes, lnaño from cont_documentos ab  where ab.id = lniddoc;
	-- Verificamos que la cuenta tiene es una cuenta de Nits. 
	select  count(*) into lncnit  from contabilidad_mayor where id = lnidmayor ;
	if lncnit>0 then	
		if lnidestado = 1 then
			-- Vamos a agregar la información.
			-- Verificamos si la cuenta auxiliar ya existe junto al año .
			select COALESCE(aa.sali,0.00),
				   COALESCE(aa.d01,0.00), COALESCE(aa.h01,0.00), COALESCE(aa.sal01,0.00),
				   COALESCE(aa.d02,0.00), COALESCE(aa.h02,0.00), COALESCE(aa.sal02,0.00),
				   COALESCE(aa.d03,0.00), COALESCE(aa.h03,0.00), COALESCE(aa.sal03,0.00),
				   COALESCE(aa.d04,0.00), COALESCE(aa.h04,0.00), COALESCE(aa.sal04,0.00),
				   COALESCE(aa.d05,0.00), COALESCE(aa.h05,0.00), COALESCE(aa.sal05,0.00),
				   COALESCE(aa.d06,0.00), COALESCE(aa.h06,0.00), COALESCE(aa.sal06,0.00),
				   COALESCE(aa.d07,0.00), COALESCE(aa.h07,0.00), COALESCE(aa.sal07,0.00),
				   COALESCE(aa.d08,0.00), COALESCE(aa.h08,0.00), COALESCE(aa.sal08,0.00),
				   COALESCE(aa.d09,0.00), COALESCE(aa.h09,0.00), COALESCE(aa.sal09,0.00),
				   COALESCE(aa.d10,0.00), COALESCE(aa.h10,0.00), COALESCE(aa.sal10,0.00),
				   COALESCE(aa.d11,0.00), COALESCE(aa.h11,0.00), COALESCE(aa.sal11,0.00),
				   COALESCE(aa.d12,0.00), COALESCE(aa.h12,0.00), COALESCE(aa.sal12,0.00),
				   COALESCE(aa.d13,0.00), COALESCE(aa.h13,0.00), COALESCE(aa.sal13,0.00),
				   COALESCE(aa.id,0) into lnsali,
				   lnd01, lnh01, lnsal01,
				   lnd02, lnh02, lnsal02,
				   lnd03, lnh03, lnsal03,
				   lnd04, lnh04, lnsal04,
				   lnd05, lnh05, lnsal05,
				   lnd06, lnh06, lnsal06,
				   lnd07, lnh07, lnsal07,
				   lnd08, lnh08, lnsal08,
				   lnd09, lnh09, lnsal09,
				   lnd10, lnh10, lnsal10,
				   lnd11, lnh11, lnsal11,
				   lnd12, lnh12, lnsal12,
				   lnd13, lnh13, lnsal13,
				   lnidtabla from contabilidad_saldosnits aa where aa.mayor_id =lnidmayor and aa.anio = lnaño and aa.personas_id = lnidpersona;
			select  count(*) into  lncontsaldo from contabilidad_saldosnits ac where ac.mayor_id = lnidmayor and ac.anio = lnaño and ac.personas_id = lnidpersona; 
			-- Si no existe, la vamos a crear
			lnsali	:=COALESCE(lnsali,0.00);
	  		lnd01	:=COALESCE(lnd01,0.00);
	   		lnh01	:=COALESCE(lnh01,0.00);
	   		lnsal01 :=COALESCE(lnsal01,0.00);
	   		lnd02	:=COALESCE(lnd02,0.00);
	   		lnh02	:=COALESCE(lnh02,0.00);
	   		lnsal02 :=COALESCE(lnsal02,0.00);
	   		lnd03	:=COALESCE(lnd03,0.00);
	   		lnh03	:=COALESCE(lnh03,0.00);
	   		lnsal03 :=COALESCE(lnsal03,0.00);
	   		lnd04	:=COALESCE(lnd04,0.00);
	   		lnh04	:=COALESCE(lnh04,0.00);
	   		lnsal04 :=COALESCE(lnsal04,0.00);
	   		lnd05	:=COALESCE(lnd05,0.00);
	   		lnh05	:=COALESCE(lnh05,0.00);
	   		lnsal05	:=COALESCE(lnsal05,0.00);
	   		lnd06	:=COALESCE(lnd06,0.00);
	   		lnh06	:=COALESCE(lnh06,0.00);
	   		lnsal06 :=COALESCE(lnsal06,0.00);
	   		lnd07	:=COALESCE(lnd07,0.00);
	   		lnh07	:=COALESCE(lnh07,0.00);
	   		lnsal07 :=COALESCE(lnsal07,0.00);
	   		lnd08	:=COALESCE(lnd08,0.00);
	   		lnh08	:=COALESCE(lnh08,0.00);
	   		lnsal08 :=COALESCE(lnsal08,0.00);
	   		lnd09	:=COALESCE(lnd09,0.00);
	   		lnh09	:=COALESCE(lnh09,0.00);
	   		lnsal09	:=COALESCE(lnsal09,0.00);
	   		lnd10	:=COALESCE(lnd10,0.00);
	   		lnh10	:=COALESCE(lnh10,0.00);
	   		lnsal10	:=COALESCE(lnsal10,0.00);
	   		lnd11	:=COALESCE(lnd11,0.00);
	   		lnh11	:=COALESCE(lnh11,0.00);
	   		lnsal11 :=COALESCE(lnsal11,0.00);
	   		lnd12	:=COALESCE(lnd12,0.00);
	   		lnh12	:=COALESCE(lnh12,0.00);
	   		lnsal12 :=COALESCE(lnsal12,0.00);
	   		lnd13	:=COALESCE(lnd13,0.00);
	   		lnh13	:=COALESCE(lnh13,0.00);
	   		lnsal13 :=COALESCE(lnsal13,0.00);	
			
			if lnmes  = 1 then
				lnd01 := lnd01 + lnvalor_db;
				lnh01 := lnh01 + lnvalor_cr;
			end if;
			if lnmes  = 2 then
				lnd02 := lnd02 + lnvalor_db;
				lnh02 := lnh02 + lnvalor_cr;
			end if;
			if lnmes  = 3 then
				lnd03 := lnd03 + lnvalor_db;
				lnh03 := lnh03 + lnvalor_cr;
			end if;
			if lnmes  = 4 then
				lnd04 := lnd04 + lnvalor_db;
				lnh04 := lnh04 + lnvalor_cr;
			end if;
			if lnmes  = 5 then
				lnd05 := lnd05 + lnvalor_db;
				lnh05 := lnh05 + lnvalor_cr;
			end if;
			if lnmes  = 6 then
				lnd06 := lnd06 + lnvalor_db;
				lnh06 := lnh06 + lnvalor_cr;
			end if;
			if lnmes  = 7 then
				lnd07 :=lnd07 + lnvalor_db;
				lnh07 := lnh07 + lnvalor_cr;
			end if;
			if lnmes  = 8 then
				lnd08 := lnd08 + lnvalor_db;
				lnh08 := lnh08 + lnvalor_cr;
			end if;
			if lnmes = 9 then
				lnd09 := lnd09 + lnvalor_db;
				lnh09 := lnh09 + lnvalor_cr;
			end if;
			if lnmes  = 10 then
				lnd10 := lnd10 + lnvalor_db;
				lnh10 := lnh10 + lnvalor_cr;
			end if;
			if lnmes  = 11 then
				lnd11 := lnd11 + lnvalor_db;
				lnh11 := lnh11 + lnvalor_cr;
			end if;
			if lnmes  = 12 and lndcierre = 0 then
				lnd12 := lnd12 + lnvalor_db;
				lnh12 := lnh12 + lnvalor_cr;
			end if;
			if lnmes  = 12 and lndcierre = 1 then
				lnd13 := lnd13 + lnvalor_db;
				lnh13 := lnh13 + lnvalor_cr;
			end if;	
			lnsal01 := lnsal01 + case when lnmes<2 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal02 := lnsal02 + case when lnmes<3 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal03 := lnsal03 + case when lnmes<4 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal04 := lnsal04 + case when lnmes<5 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal05 := lnsal05 + case when lnmes<6 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal06 := lnsal06 + case when lnmes<7 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal07 := lnsal07 + case when lnmes<8 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal08 := lnsal08 + case when lnmes<9 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal09 := lnsal09 + case when lnmes<10 then (lnvalor_db - lnvalor_cr)else 0 end;
			lnsal10 := lnsal10 + case when lnmes<11 then (lnvalor_db - lnvalor_cr)else 0 end;
			lnsal11 := lnsal11 + case when lnmes<12 then (lnvalor_db - lnvalor_cr)else 0 end;
			lnsal12 := lnsal12 + case when lnmes<13 and lndcierre=0 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal13 := lnsal13 + case when lnmes<13 then (lnvalor_db - lnvalor_cr) else 0 end;
	
			if lncontsaldo = 0 then
				Insert into contabilidad_saldosnits ( anio, mayor_id, personas_id, sali,
										 	   d01, h01, sal01,
										 	   d02, h02, sal02,
										 	   d03, h03, sal03,
										 	   d04, h04, sal04,
										 	   d05, h05, sal05,
										  	   d06, h06, sal06,
										  	   d07, h07, sal07,
										 	   d08, h08, sal08,
										  	   d09, h09, sal09,
										 	   d10, h10, sal10,
										  	   d11, h11, sal11,
										  	   d12, h12, sal12,
										   	   d13, h13, sal13)values 
											 ( lnaño, lnidmayor,lnidpersona, lnsali,
										  	   lnd01, lnh01, lnsal01,
										  	   lnd02, lnh02, lnsal02,
										 	   lnd03, lnh03, lnsal03,
										  	   lnd04, lnh04, lnsal04,
										  	   lnd05, lnh05, lnsal05,
										 	   lnd06, lnh06, lnsal06,
										 	   lnd07, lnh07, lnsal07,
										 	   lnd08, lnh08, lnsal08,
											   lnd09, lnh09, lnsal09,
											   lnd10, lnh10, lnsal10,
										 	   lnd11, lnh11, lnsal11,
										 	   lnd12, lnh12, lnsal12,
										 	   lnd13, lnh13, lnsal13);																		 
			else
				update contabilidad_saldosnits set 
				d01= lnd01, h01= lnh01, sal01 = lnsal01,
				d02= lnd02, h02= lnh02, sal02 = lnsal02,
				d03= lnd03, h03= lnh03, sal03 = lnsal03,
				d04= lnd04, h04= lnh04, sal04 = lnsal04,
				d05= lnd05, h05= lnh05, sal05 = lnsal05,
				d06= lnd06, h06= lnh06, sal06 = lnsal06,
				d07= lnd07, h07= lnh07, sal07 = lnsal07,
				d08= lnd08, h08= lnh08, sal08 = lnsal08,
				d09= lnd09, h09= lnh09, sal09 = lnsal09,
				d10= lnd10, h10= lnh10, sal10 = lnsal10,
				d11= lnd11, h11= lnh11, sal11 = lnsal11,
				d12= lnd12, h12= lnh12, sal12 = lnsal12,
				d13= lnd13, h13= lnh13, sal13 = lnsal13
				where id = lnidtabla;
			end if ;
		end if;
		if lnidestado = 2 then
			-- Vamosa agregar la información.
			-- Verificamos si la cuenta auxiliar ya existe junto al año .
			Select COALESCE(aa.d01,0.00), COALESCE(aa.h01,0.00), COALESCE(aa.sal01,0.00),
				   COALESCE(aa.d02,0.00), COALESCE(aa.h02,0.00), COALESCE(aa.sal02,0.00),
				   COALESCE(aa.d03,0.00), COALESCE(aa.h03,0.00), COALESCE(aa.sal03,0.00),
				   COALESCE(aa.d04,0.00), COALESCE(aa.h04,0.00), COALESCE(aa.sal04,0.00),
				   COALESCE(aa.d05,0.00), COALESCE(aa.h05,0.00), COALESCE(aa.sal05,0.00),
				   COALESCE(aa.d06,0.00), COALESCE(aa.h06,0.00), COALESCE(aa.sal06,0.00),
				   COALESCE(aa.d07,0.00), COALESCE(aa.h07,0.00), COALESCE(aa.sal07,0.00),
				   COALESCE(aa.d08,0.00), COALESCE(aa.h08,0.00), COALESCE(aa.sal08,0.00),
				   COALESCE(aa.d09,0.00), COALESCE(aa.h09,0.00), COALESCE(aa.sal09,0.00),
				   COALESCE(aa.d10,0.00), COALESCE(aa.h10,0.00), COALESCE(aa.sal10,0.00),
				   COALESCE(aa.d11,0.00), COALESCE(aa.h11,0.00), COALESCE(aa.sal11,0.00),
				   COALESCE(aa.d12,0.00), COALESCE(aa.h12,0.00), COALESCE(aa.sal12,0.00),
				   COALESCE(aa.d13,0.00), COALESCE(aa.h13,0.00), COALESCE(aa.sal13,0.00),
				   COALESCE(aa.id,0) into 
				   lnd01, lnh01, lnsal01,
				   lnd02, lnh02, lnsal02,
				   lnd03, lnh03, lnsal03,
				   lnd04, lnh04, lnsal04,
				   lnd05, lnh05, lnsal05,
				   lnd06, lnh06, lnsal06,
				   lnd07, lnh07, lnsal07,
				   lnd08, lnh08, lnsal08,
				   lnd09, lnh09, lnsal09,
				   lnd10, lnh10, lnsal10,
				   lnd11, lnh11, lnsal11,
				   lnd12, lnh12, lnsal12,
				   lnd13, lnh13, lnsal13,
				   lnidtabla from contabilidad_saldosnits aa where aa.mayor_id =lnidmayor and aa.anio = lnaño and aa.personas_id = lnidpersona ;
			select  count(*) into  lncontsaldo from contabilidad_saldosnits ac where ac.mayor_id = lnidmayor and ac.anio = lnaño and ac.personas_id = lnidpersona; 
			-- Si no existe, la vamos a crear
			lnsali	:=COALESCE(lnsali,0.00);
	  		lnd01	:=COALESCE(lnd01,0.00);
	   		lnh01	:=COALESCE(lnh01,0.00);
	   		lnsal01 :=COALESCE(lnsal01,0.00);
	   		lnd02	:=COALESCE(lnd02,0.00);
	   		lnh02	:=COALESCE(lnh02,0.00);
	   		lnsal02 :=COALESCE(lnsal02,0.00);
	   		lnd03	:=COALESCE(lnd03,0.00);
	   		lnh03	:=COALESCE(lnh03,0.00);
	   		lnsal03 :=COALESCE(lnsal03,0.00);
	   		lnd04	:=COALESCE(lnd04,0.00);
	   		lnh04	:=COALESCE(lnh04,0.00);
	   		lnsal04 :=COALESCE(lnsal04,0.00);
	   		lnd05	:=COALESCE(lnd05,0.00);
	   		lnh05	:=COALESCE(lnh05,0.00);
	   		lnsal05	:=COALESCE(lnsal05,0.00);
	   		lnd06	:=COALESCE(lnd06,0.00);
	   		lnh06	:=COALESCE(lnh06,0.00);
	   		lnsal06 :=COALESCE(lnsal06,0.00);
	   		lnd07	:=COALESCE(lnd07,0.00);
	   		lnh07	:=COALESCE(lnh07,0.00);
	   		lnsal07 :=COALESCE(lnsal07,0.00);
	   		lnd08	:=COALESCE(lnd08,0.00);
	   		lnh08	:=COALESCE(lnh08,0.00);
	   		lnsal08 :=COALESCE(lnsal08,0.00);
	   		lnd09	:=COALESCE(lnd09,0.00);
	   		lnh09	:=COALESCE(lnh09,0.00);
	   		lnsal09	:=COALESCE(lnsal09,0.00);
	   		lnd10	:=COALESCE(lnd10,0.00);
	   		lnh10	:=COALESCE(lnh10,0.00);
	   		lnsal10	:=COALESCE(lnsal10,0.00);
	   		lnd11	:=COALESCE(lnd11,0.00);
	   		lnh11	:=COALESCE(lnh11,0.00);
	   		lnsal11 :=COALESCE(lnsal11,0.00);
	   		lnd12	:=COALESCE(lnd12,0.00);
	   		lnh12	:=COALESCE(lnh12,0.00);
	   		lnsal12 :=COALESCE(lnsal12,0.00);
	   		lnd13	:=COALESCE(lnd13,0.00);
	   		lnh13	:=COALESCE(lnh13,0.00);
	   		lnsal13 :=	COALESCE(lnsal13,0.00);				
			if lnmes = 1 then
				lnd01 = lnd01 - lnvalor_db ;
				lnh01 = lnh01 - lnvalor_cr ;
			end if ;
			if lnmes = 2 then
				lnd02 := lnd02 - lnvalor_db;
				lnh02 := lnh02 - lnvalor_cr;
			end if ;
			if lnmes = 3 then
				lnd03 := lnd03 - lnvalor_db;
				lnh03 := lnh03 - lnvalor_cr;
			end if ;
			if lnmes = 4 then
				lnd04 := lnd04 - lnvalor_db;
				lnh04 := lnh04 - lnvalor_cr;
			end if ;
			if lnmes = 5 then
				lnd05 := lnd05 - lnvalor_db;
				lnh05 := lnh05 - lnvalor_cr;
			end if ;
			if lnmes = 6 then
				lnd06 := lnd06 - lnvalor_db;
				lnh06 := lnh06 - lnvalor_cr;
			end if ;
			if lnmes = 7 then
				lnd07 := lnd07 - lnvalor_db;
				lnh07 := lnh07 - lnvalor_cr;
			end if ;
			if lnmes = 8 then
				lnd08 := lnd08 - lnvalor_db;
				lnh08 := lnh08 - lnvalor_cr;
			end if ;
			if lnmes = 9 then
				lnd09 := lnd09 - lnvalor_db;
				lnh09 := lnh09 - lnvalor_cr;
			end if ;
			if lnmes = 10 then
				lnd10 := lnd10 - lnvalor_db;
				lnh10 := lnh10 - lnvalor_cr;
			end if ;
			if lnmes = 11 then  
				lnd11 := lnd11 - lnvalor_db;
				lnh11 := lnh11 - lnvalor_cr;
			end if ;
			if lnmes = 12 and lndcierre=0 then
				lnd12 := lnd12 - lnvalor_db;
				lnh12 := lnh12 - lnvalor_cr;
			end if ;
			if lnmes = 12 and lndcierre=1 then
				lnd13 := lnd13 - lnvalor_db;
				lnh13 := lnh13 - lnvalor_cr;
			end if ;			
			lnsal01 := lnsal01 - case when lnmes<2 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal02 := lnsal02 - case when lnmes<3 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal03 := lnsal03 - case when lnmes<4 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal04 := lnsal04 - case when lnmes<5 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal05 := lnsal05 - case when lnmes<6 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal06 := lnsal06 - case when lnmes<7 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal07 := lnsal07 - case when lnmes<8 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal08 := lnsal08 - case when lnmes<9 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal09 := lnsal09 - case when lnmes<10 then (lnvalor_db - lnvalor_cr)else 0 end;
			lnsal10 := lnsal10 - case when lnmes<11 then (lnvalor_db - lnvalor_cr)else 0 end;
			lnsal11 := lnsal11 - case when lnmes<12 then (lnvalor_db - lnvalor_cr)else 0 end;
			lnsal12 := lnsal12 - case when lnmes<13 and lndcierre=0 then (lnvalor_db - lnvalor_cr) else 0 end;
			lnsal13 := lnsal13 - case when lnmes<13  then (lnvalor_db - lnvalor_cr) else 0 end;
	
			update contabilidad_saldosnits set 
				d01= lnd01, h01= lnh01, sal01 = lnsal01,
				d02= lnd02, h02= lnh02, sal02 = lnsal02,
				d03= lnd03, h03= lnh03, sal03 = lnsal03,
				d04= lnd04, h04= lnh04, sal04 = lnsal04,
				d05= lnd05, h05= lnh05, sal05 = lnsal05,
				d06= lnd06, h06= lnh06, sal06 = lnsal06,
				d07= lnd07, h07= lnh07, sal07 = lnsal07,
				d08= lnd08, h08= lnh08, sal08 = lnsal08,
				d09= lnd09, h09= lnh09, sal09 = lnsal09,
				d10= lnd10, h10= lnh10, sal10 = lnsal10,
				d11= lnd11, h11= lnh11, sal11 = lnsal11,
				d12= lnd12, h12= lnh12, sal12 = lnsal12, 
				d13= lnd13, h13= lnh13, sal13 = lnsal13 
				where id = lnidtabla ;
		end if;
	END	if ;
	RETURN NULL;
END;
$function$;

DROP TRIGGER IF EXISTS trg_mayorizarnit ON contabilidad_mov;
CREATE TRIGGER trg_mayorizarnit
    AFTER INSERT OR UPDATE ON contabilidad_mov
    FOR EACH ROW
    EXECUTE FUNCTION public.tg_mayorizarnit();


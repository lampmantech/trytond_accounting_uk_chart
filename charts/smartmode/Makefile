
WD=$(PWD)

# If you have Oerp 7.0 installed, set the following path to the addons
OERP_7_ADDONS=/n/src/openerp-7.0-20140125-002455/openerp/addons

# Install the chart converter alongside where you installed this module
CHART_CONVERTER=../../../trytond_chart_converter
#CHART_CONVERTER=/g/TrytonOpenERP/3.6/trytond_chart_converter

default::	accounting_uk_chart_smartmode_CoAs.xml

# copy the original files from OERP7 and convert them to Unix
orig::
	[ ! -d $(OERP_7_ADDONS) ] || \
	for file in $(OERP_7_ADDONS)/l10n_uk/data/a*.csv ; do \
		base=`basename "$$file"` ; \
		[ -f "$$base".orig ] || \
		  dos2unix < $$file > "$$base".orig  ; \
	    done

# clean up their csv
csv:: orig
	for file in *.orig ; do \
		base=`basename "$$file" .orig` ; \
		[ -f "$$base".csv ] || \
		  sed -f commas_in_csv.sed \
		    < "$$file" > "$$base"  ; \
	    done

# apply some patches - read the patch files for details
patch:: csv
	for file in *.patch ; do \
		base=`basename "$$file" .patch` ; \
		[ -f "$$base".dst ] || \
		  patch -p 0 -b -z .dst "$$base" \
		    < "$$file"  ; \
	    done

# convert them to openerp7 xml from csv
accounting_uk_chart_smartmode.ascii:: patch \
		$(CHART_CONVERTER)/charts/openerp7-l10n_uk-csv-to-xml.sh
	( cd $(CHART_CONVERTER)/charts ; \
	 	sh openerp7-l10n_uk-csv-to-xml.sh "$(WD)" \
		| sed -e 's@<\([^<>]* ref=""[^<>]*\)>@<!-- \0 -->@' \
		> "$(WD)/$@" )

accounting_uk_chart_smartmode.cfg:: $(CHART_CONVERTER)/en.cfg
	sed -e "s@xmlfile = @xmlfile = $(CHART_CONVERTER)/charts/@" $< > $@

# convert them to Tryton xml from openerp7
accounting_uk_chart_smartmode_CoAs.xml:: accounting_uk_chart_smartmode.ascii \
		accounting_uk_chart_smartmode.cfg \
		$(CHART_CONVERTER)/converter.py
	( cd $(CHART_CONVERTER) ; \
	 	python converter.py --lang=en \
			-c $(WD)/accounting_uk_chart_smartmode.cfg \
			-x $(WD)/accounting_uk_chart_smartmode_CoTs.xml \
			-o "$(WD)/$@" "$(WD)/$<" )

# clean up intermediate files
clean::
	rm -f *~  *.dst *.ascii

# remove the copies from OpenERP7
veryclean:: clean
	rm -f *.orig *.csv

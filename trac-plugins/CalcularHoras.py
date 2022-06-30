import json
import copy
import re
import datetime

from urllib import urlencode
from genshi.builder import tag
from trac.wiki.macros import WikiMacroBase

GOOGLE_CHART_API_URL = 'http://chart.apis.google.com/chart?'
GRINCH_URL = 'http://netlandish.grinchapp.com/history/'


class CalcularHorasMacro(WikiMacroBase):
    """Simple HelloWorld macro.

    Note that the name of the class is meaningful:
     - it must end with "Macro"
     - what comes before "Macro" ends up being the macro name

    The documentation of the class (i.e. what you're reading)
    will become the documentation of the macro, as shown by
    the !MacroList macro (usually used in the WikiMacros page).
    """

    def expand_macro(self, formatter, name, args):
        """Return some output that will be displayed in the Wiki content.

        `name` is the actual name of the macro (no surprise, here it'll be
        `'HelloWorld'`),
        `args` is the text enclosed in parenthesis at the call of the macro.
          Note that if there are ''no'' parenthesis (like in, e.g.
          [[HelloWorld]]), then `args` is `None`.
        """
        self.data = {}
        self.hours = {}

        total, horas_semanas = self.get_total_hours(formatter.source)

        for arg in args.split(', '):
            k, v  = arg.split('=')
            self.data[k] = v
        self.data['valor_hora'] = float(self.data['valor_hora'])
        return self.get_html(total, horas_semanas)

    def get_section_hours(self, content):
        regex = r'(?P<hour>\d\d?)(?::(?P<minutes>\d\d))?hs( \((?P<project>[\w -]+)\))?'
        hours = re.findall(regex, content)
        # hours = re.findall(r'(\d\d?):(\d\d)hs|(\d\d?)hs', content)
        # import ipdb;ipdb.set_trace()

        total = 0
        for h in hours:
            if h[-1] not in self.hours:
                self.hours[h[-1]] = 0

            hours_to_log = int(h[0])
            try:
                # horas:minutos
                minutes_to_log = int(h[1]) / 60.0
                time_to_log = hours_to_log + minutes_to_log
                total += time_to_log
            except ValueError:
                # horas enteras
                time_to_log = hours_to_log
                total += time_to_log

            self.hours[h[-1]] += time_to_log
        return total

    def get_total_hours(self, content):
        semanas = content.split('----')
        horas_semanas = dict()
        for i, s in enumerate(semanas):
            horas_semanas[i] = self.get_section_hours(s)
        total = sum(horas_semanas.values())

        return total, horas_semanas

    def get_html(self, total, horas_semanas):
        valor_hora = self.data['valor_hora']
        text = ['Horas trabajadas: %.2f' % total,
                'Precio en dolares (U$S%s): %.2f' % (valor_hora, total * valor_hora)]
        text.extend(['Horas semana %s: %.2f' % (nro+1, horas) for nro, horas in horas_semanas.items()])
        div = tag.div()
        ul = tag.ul()
        for li in text:
            ul.append(tag.li(li))

        if 'date' in self.data:
            link = tag.a('@netlandish: Grinch report',
                         href=self._get_grinch_report_url())
            ul.append(link)
        div.append(ul)

        img = tag.img(src=self._get_google_chart(horas_semanas))
        div.append(img)

        ul = tag.ul()
        for project, hours in self.hours.iteritems():
            ul.append(tag.li('{0}: {1}'.format(project.title(), hours)))
        div.append(ul)

        return div

    def _get_google_chart(self, horas_semanas):
        data = {}
        data['cht'] = 'bvs' # grafico de barras
        # FIXME: necesito ordenar el diccionario de horas por el numero de semana
        data['chd'] = 't:' + ','.join([str(v) for k,v in horas_semanas.items()])  # datos
        data['chs'] = '150x100' # png size
        data['chds'] = '0,45' 
        data['chxr'] = '1,0,45' # y-scale
        data['chxl'] = '0:|1|2|3|4|5' # x-label
        data['chxt'] = 'x,y' # labels

        url = GOOGLE_CHART_API_URL + urlencode(data)
        return url

    def _get_grinch_report_url(self):
        date = self.data['date']
        return GRINCH_URL + '?' + urlencode({
            'start_date': date + '-01',
            'end_date': date + '-31',
            'submit': 'Filter+Entries'
        })

    # Note that there's no need to HTML escape the returned data,
    # as the template engine (Genshi) will do it for us.

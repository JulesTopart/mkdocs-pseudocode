import logging
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import re

log = logging.getLogger('mkdocs.plugins.pseudocode')

class PseudocodePlugin(BasePlugin):
    config_scheme = (
        ('syntax', config_options.Type(str, default='pseudocode')),
    )

    def __init__(self):
        self.number = 0
        self.indent_level = 0
        self.open_divs = []

    def on_page_markdown(self, markdown, page, config, files):
        self.number = 0
        log.debug('Processing page: %s', page.file.abs_src_path)
        return self.convert_pseudocode_blocks(markdown)

    def convert_pseudocode_blocks(self, markdown_text):
        log.debug('Converting pseudocode blocks')

        def pseudocode_replacer(match):
            code = match.group(1)
            html = self.render_pseudocode(code)
            return f'\n\n{html}\n\n'

        pseudocode_block_pattern = re.compile(r'```pseudocode\n(.*?)```', re.DOTALL)
        return re.sub(pseudocode_block_pattern, pseudocode_replacer, markdown_text)

    def render_pseudocode(self, code):
        lines = code.strip().split('\n')
        self.indent_level = 0
        self.open_divs = []
        html_lines = ["<div class='ps-root'>"]

        handlers = {
            r"\begin{algorithm}": self._handle_begin_algorithm,
            r"\end{algorithm}": self._handle_end_algorithm,
            r"\caption{": self._handle_caption,
            r"\begin{algorithmic}": self._handle_begin_algorithmic,
            r"\end{algorithmic}": self._handle_end_algorithmic,
            r"\PROCEDURE{": self._handle_procedure,
            r"\ENDPROCEDURE": self._handle_end_procedure,
            r"\IF{": self._handle_if,
            r"\ENDIF": self._handle_end_if,
            r"\FOREACH{": self._handle_foreach,
            r"\ENDFOREACH": self._handle_end_foreach,
            r"\FOR{": self._handle_for,
            r"\ENDFOR": self._handle_end_for,
            r"\WHILE{": self._handle_while,
            r"\ENDWHILE": self._handle_end_while,
            r"\REPEAT{": self._handle_repeat,
            r"\ENDREPEAT": self._handle_end_repeat,
            r"\ELSEIF{": self._handle_elseif,
            r"\ELSE": self._handle_else,
            r"\STATE": self._handle_state,
            r"\CALL{": self._handle_call,
        }

        for line in lines:
            stripped_line = line.strip()
            for pattern, handler in handlers.items():
                if stripped_line.startswith(pattern):
                    handler(stripped_line, html_lines)
                    break

        while self.open_divs:
            html_lines.append(f"</div>")
            self.open_divs.pop()

        html_lines.append("</div>")  # Close pseudocode div
        return "\n".join(html_lines)

    def _handle_begin_algorithm(self, line, html_lines):
        html_lines.append("<div class='ps-algorithm'>")
        self.open_divs.append('algorithm')

    def _handle_end_algorithm(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'algorithm':
            html_lines.append("</div>")
            self.open_divs.pop()

    def _handle_caption(self, line, html_lines):
        caption = re.search(r'\{(.*?)\}', line).group(1)
        html_lines[-1] = f"<div class='ps-algorithm with-caption'><div class='ps-caption'><span class='ps-keyword'>Algorithm {self.number}</span> {caption}</div>"

    def _handle_begin_algorithmic(self, line, html_lines):
        html_lines.append("<div class='ps-algorithmic'>")
        self.open_divs.append('algorithmic')

    def _handle_end_algorithmic(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'algorithmic':
            html_lines.append("</div>")
            self.open_divs.pop()

    def _handle_procedure(self, line, html_lines):
        procedure_name = re.search(r'\{(.*?)\}', line).group(1)
        params = re.search(r'\}\{(.*?)\}', line).group(1)
        params = self._wrap_math_expressions(params)
        html_lines.append(f"<div class='ps-procedure ps-indent-{self.indent_level}'><span class='ps-keyword'>procedure </span><span class='ps-funcname'>{procedure_name}</span>({params})")
        self.open_divs.append('procedure')
        self.indent_level += 1

    def _handle_end_procedure(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'procedure':
            self.indent_level -= 1
            html_lines.append(f"<div class='ps-keyword'>end procedure</div></div>")
            self.open_divs.pop()

    def _handle_if(self, line, html_lines):
        condition = re.search(r'\{(.*?)\}', line).group(1)
        statement = self._process_control_statement('if', condition)
        html_lines.append(statement)
        self.open_divs.append('if')
        self.indent_level += 1

    def _handle_end_if(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'if':
            self.indent_level -= 1
            html_lines.append(f"<div class='ps-keyword'>end if</div></div>")
            self.open_divs.pop()

    def _handle_for(self, line, html_lines):
        loop = re.search(r'\{(.*?)\}', line).group(1)
        statement = self._process_control_statement('for', loop)
        html_lines.append(statement)
        self.open_divs.append('for')
        self.indent_level += 1

    def _handle_end_for(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'for':
            self.indent_level -= 1
            html_lines.append(f"<div class='ps-keyword'>end for</div></div>")
            self.open_divs.pop()

    def _handle_end_foreach(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'foreach':
            self.indent_level -= 1
            html_lines.append(f"<div class='ps-keyword'>end foreach</div></div>")
            self.open_divs.pop()

    def _handle_foreach(self, line, html_lines):
        loop = re.search(r'\{(.*?)\}', line).group(1)
        statement = self._process_control_statement('foreach', loop)
        html_lines.append(statement)
        self.open_divs.append('foreach')
        self.indent_level += 1

    def _handle_while(self, line, html_lines):
        condition = re.search(r'\{(.*?)\}', line).group(1)
        statement = self._process_control_statement('while', condition)
        html_lines.append(statement)
        self.open_divs.append('while')
        self.indent_level += 1

    def _handle_end_while(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'while':
            self.indent_level -= 1
            html_lines.append(f"<div class='ps-keyword'>end while</div></div>")
            self.open_divs.pop()

    def _handle_repeat(self, line, html_lines):
        condition = re.search(r'\{(.*?)\}', line).group(1)
        statement = self._process_control_statement('repeat', condition)
        html_lines.append(statement)
        self.open_divs.append('repeat')
        self.indent_level += 1

    def _handle_end_repeat(self, line, html_lines):
        if self.open_divs and self.open_divs[-1] == 'repeat':
            self.indent_level -= 1
            html_lines.append(f"<div class='ps-keyword'>end repeat</div></div>")
            self.open_divs.pop()

    def _handle_elseif(self, line, html_lines):
        condition = re.search(r'\{(.*?)\}', line).group(1)
        statement = self._process_control_statement('elseif', condition)
        html_lines.append(statement)
        if self.open_divs and self.open_divs[-1] == 'if':
            self.open_divs.pop()
            self.open_divs.append('elseif')

    def _handle_else(self, line, html_lines):
        html_lines.append(f"<div class='ps-else ps-indent-{self.indent_level}'><span class='ps-keyword'>else</span>")
        if self.open_divs and self.open_divs[-1] in ['if', 'elseif']:
            self.open_divs.pop()
            self.open_divs.append('else')

    def _handle_state(self, line, html_lines):
        statement = line[len(r"\STATE "):]
        statement = self._replace_calls(statement)
        statement = self._wrap_math_expressions(statement)
        html_lines.append(f"<div class='ps-state ps-indent-{self.indent_level}'>{statement}</div>")

    def _handle_call(self, line, html_lines):
        call = re.search(r'\{(.*?)\}', line).group(1)
        params = re.search(r'\}\{(.*?)\}', line).group(1)
        html_lines.append(f"<div class='ps-call ps-indent-{self.indent_level}'><span class='ps-funcname'>{call}</span>({params})</div>")

    def _replace_calls(self, statement):
        call_pattern = re.compile(r'\\CALL\{(.*?)\}\{(.*?)\}')
        return call_pattern.sub(r'<span class="ps-call"><span class="ps-funcname">\1</span>(\2)</span>', statement)

    def _wrap_math_expressions(self, statement):
        return re.sub(r'\$(.*?)\$', r'<span class="arithmatex">\\(\1\\)</span>', statement)

    def _process_control_statement(self, keyword, condition):
        condition = self._wrap_math_expressions(condition)
        additional_keyword = "then" if keyword == "if" else "do"
        if keyword == "for":
            condition = condition.replace(r'\TO', '<span class="ps-keyword">to</span>')
        elif keyword == "foreach":
            condition = condition.replace(r'\IN', '<span class="ps-keyword">in</span>')
        return f"<div class='ps-{keyword.lower()} ps-indent-{self.indent_level}'><span class='ps-keyword'>{keyword.lower()}</span> ({condition}) <span class='ps-keyword'>{additional_keyword}</span>"

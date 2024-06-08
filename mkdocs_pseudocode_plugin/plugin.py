import logging
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import re

log = logging.getLogger('mkdocs.plugins.pseudocode')

class PseudocodePlugin(BasePlugin):
    config_scheme = (
        ('syntax', config_options.Type(str, default='pseudocode')),
    )

    number = 0

    def on_page_markdown(self, markdown, page, config, files):
        self.number = 0
        log.debug('Processing page: %s', page.file.abs_src_path)
        new_markdown = self.convert_pseudocode_blocks(markdown)
        return new_markdown

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
        html_lines = ["<div class='ps-root'>"]
        self.number = self.number + 1
        open_divs = []
        algorithm_name = "Algorithm"
        indent_level = 0

        call_pattern = re.compile(r'\\CALL\{(.*?)\}\{(.*?)\}')

        def replace_calls(statement):
            return call_pattern.sub(r'<span class="ps-call"><span class="ps-funcname">\1</span>(\2)</span>', statement)

        def wrap_math_expressions(statement):
            return re.sub(r'\$(.*?)\$', r'<span class="arithmatex">\\(\1\\)</span>', statement)

        def process_control_statement(keyword, condition):
            condition = wrap_math_expressions(condition)
            additional_keyword = "then" if keyword == "if" else "do"
            if keyword == "for":
                condition = condition.replace(r'\TO', '<span class="ps-keyword">to</span>')
            return f"<div class='ps-{keyword.lower()} ps-indent-{indent_level}'><span class='ps-keyword'>{keyword.lower()}</span> ({condition}) <span class='ps-keyword'>{additional_keyword}</span>"

        i = 0
        while i < len(lines):
            stripped_line = lines[i].strip()
            if stripped_line.startswith(r"\begin{algorithm}"):
                html_lines.append("<div class='ps-algorithm'>")
                open_divs.append('algorithm')
            elif stripped_line.startswith(r"\end{algorithm}"):
                if open_divs and open_divs[-1] == 'algorithm':
                    html_lines.append("</div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\caption{"):
                caption = re.search(r'\{(.*?)\}', stripped_line).group(1)
                html_lines[-1] = f"<div class='ps-algorithm with-caption'><div class='ps-caption'><span class='ps-keyword'>Algorithm {self.number}</span> {caption}</div>"
            elif stripped_line.startswith(r"\begin{algorithmic}"):
                html_lines.append("<div class='ps-algorithmic'>")
                open_divs.append('algorithmic')
            elif stripped_line.startswith(r"\end{algorithmic}"):
                if open_divs and open_divs[-1] == 'algorithmic':
                    html_lines.append("</div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\PROCEDURE{"):
                procedure_name = re.search(r'\{(.*?)\}', stripped_line).group(1)
                params = re.search(r'\}\{(.*?)\}', stripped_line).group(1)
                params = wrap_math_expressions(params)
                html_lines.append(f"<div class='ps-procedure ps-indent-{indent_level}'><span class='ps-keyword'>procedure </span><span class='ps-funcname'>{procedure_name}</span>({params})")
                open_divs.append('procedure')
                indent_level += 1
            elif stripped_line.startswith(r"\ENDPROCEDURE"):
                if open_divs and open_divs[-1] == 'procedure':
                    indent_level -= 1
                    html_lines.append(f"<div class='ps-keyword'>end procedure</div></div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\IF{"):
                condition = re.search(r'\{(.*?)\}', stripped_line).group(1)
                statement = process_control_statement('if', condition)
                html_lines.append(statement)
                open_divs.append('if')
                indent_level += 1
            elif stripped_line.startswith(r"\ENDIF"):
                if open_divs and open_divs[-1] == 'if':
                    indent_level -= 1
                    html_lines.append(f"<div class='ps-keyword'>end if</div></div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\FOR{"):
                loop = re.search(r'\{(.*?)\}', stripped_line).group(1)
                statement = process_control_statement('for', loop)
                html_lines.append(statement)
                open_divs.append('for')
                indent_level += 1
            elif stripped_line.startswith(r"\ENDFOR"):
                if open_divs and open_divs[-1] == 'for':
                    indent_level -= 1
                    html_lines.append(f"<div class='ps-keyword'>end for</div></div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\FOREACH{"):
                loop = re.search(r'\{(.*?)\}', stripped_line).group(1)
                statement = f"<div class='ps-foreach ps-indent-{indent_level}'><span class='ps-keyword'>for each</span> ({wrap_math_expressions(loop)}) <span class='ps-keyword'>do</span>"
                html_lines.append(statement)
                open_divs.append('foreach')
                indent_level += 1
            elif stripped_line.startswith(r"\ENDFOREACH"):
                if open_divs and open_divs[-1] == 'foreach':
                    indent_level -= 1
                    html_lines.append(f"<div class='ps-keyword'>end for each</div></div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\WHILE{"):
                condition = re.search(r'\{(.*?)\}', stripped_line).group(1)
                statement = process_control_statement('while', condition)
                html_lines.append(statement)
                open_divs.append('while')
                indent_level += 1
            elif stripped_line.startswith(r"\ENDWHILE"):
                if open_divs and open_divs[-1] == 'while':
                    indent_level -= 1
                    html_lines.append(f"<div class='ps-keyword'>end while</div></div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\REPEAT{"):
                condition = re.search(r'\{(.*?)\}', stripped_line).group(1)
                statement = process_control_statement('repeat', condition)
                html_lines.append(statement)
                open_divs.append('repeat')
                indent_level += 1
            elif stripped_line.startswith(r"\ENDREPEAT"):
                if open_divs and open_divs[-1] == 'repeat':
                    indent_level -= 1
                    html_lines.append(f"<div class='ps-keyword'>end repeat</div></div>")
                    open_divs.pop()
            elif stripped_line.startswith(r"\ELSEIF{"):
                condition = re.search(r'\{(.*?)\}', stripped_line).group(1)
                statement = process_control_statement('elseif', condition)
                html_lines.append(statement)
                if open_divs and open_divs[-1] == 'if':
                    open_divs.pop()
                    open_divs.append('elseif')
            elif stripped_line.startswith(r"\ELSE"):
                html_lines.append(f"<div class='ps-else ps-indent-{indent_level}'><span class='ps-keyword'>else</span>")
                if open_divs and open_divs[-1] in ['if', 'elseif']:
                    open_divs.pop()
                    open_divs.append('else')
            elif stripped_line.startswith(r"\STATE"):
                statement = stripped_line[len(r"\STATE "):]
                statement = replace_calls(statement)
                statement = wrap_math_expressions(statement)
                html_lines.append(f"<div class='ps-state ps-indent-{indent_level}'>{statement}</div>")
            elif stripped_line.startswith(r"\CALL{"):
                call = re.search(r'\{(.*?)\}', stripped_line).group(1)
                params = re.search(r'\}\{(.*?)\}', stripped_line).group(1)
                html_lines.append(f"<div class='ps-call ps-indent-{indent_level}'><span class='ps-funcname'>{call}</span>({params})</div>")
            
            i += 1

        while open_divs:
            html_lines.append(f"</div>")
            open_divs.pop()

        html_lines.append("</div>")  # Close pseudocode div
        return "\n".join(html_lines)

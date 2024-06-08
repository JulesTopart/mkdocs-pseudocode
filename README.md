# MkDocs Pseudocode Plugin

This MkDocs plugin allows you to write beautiful pseudocode in your MkDocs documentation using a simplified syntax inspired by LaTeX.

## Features

- Render pseudocode blocks with LaTeX-inspired syntax
- Support for common control structures (`if`, `for`, `while`, `repeat`, `foreach`)
- Math expressions rendered using MathJax
- Nested procedures and calls
- Automatic indentation and keyword highlighting

## Installation

1. Install the plugin locally:

   ```bash
   pip install mkdocs-pseudocode
   ```

2. Add the plugin to your `mkdocs.yml` configuration file:

   ```yaml
   plugins:
     - search
     - pseudocode
   ```

3. Copy CSS file into your `extra.css` file of your Mkdocs project

    Place the `pseudo-code.css` file in the `docs/css/` directory of your MkDocs project.

    Add the following lines to your `mkdocs.yml` file:

    ```yaml
    extra_css:
        - css/pseudo-code.css
    ```

## Usage

Write your pseudocode in fenced code blocks with the `pseudocode` language identifier:

```markdown
```pseudocode
% This quicksort algorithm is extracted from Chapter 7, Introduction to Algorithms (3rd edition)
\begin{algorithm}
\caption{Quicksort}
\begin{algorithmic}
\PROCEDURE{Quicksort}{$A, p, r$}
    \IF{$p < r$} 
        \STATE $q = $ \CALL{Partition}{$A, p, r$}
        \STATE \CALL{Quicksort}{$A, p, q - 1$}
        \STATE \CALL{Quicksort}{$A, q + 1, r$}
    \ENDIF
\ENDPROCEDURE
\PROCEDURE{Partition}{$A, p, r$}
    \STATE $x = A[r]$
    \STATE $i = p - 1$
    \FOR{$j = p$ \TO $r - 1$}
        \IF{$A[j] < x$}
            \STATE $i = i + 1$
            \STATE exchange $A[i]$ with $A[j]$
        \ENDIF
    \ENDFOR
    \STATE exchange $A[i]$ with $A[r]$
\ENDPROCEDURE
\end{algorithmic}
\end{algorithm}
```

## Customization

### CSS

You can customize the appearance of the pseudocode by adding your own CSS rules. The default CSS classes used are:

- `.ps-root`
- `.ps-algorithm`
- `.ps-algorithmic`
- `.ps-caption`
- `.ps-keyword`
- `.ps-procedure`
- `.ps-if`
- `.ps-for`
- `.ps-while`
- `.ps-repeat`
- `.ps-foreach`
- `.ps-state`
- `.ps-call`
- `.ps-funcname`
- `.ps-indent-{level}`

### JavaScript

To ensure MathJax expressions are rendered correctly, you may need to add the following JavaScript snippet to your MkDocs theme:

```html
<script>
document.addEventListener("DOMContentLoaded", function() {
    if (typeof MathJax !== 'undefined') {
        MathJax.typesetPromise();
    }
});
</script>
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## Author

Jules TOPART

---
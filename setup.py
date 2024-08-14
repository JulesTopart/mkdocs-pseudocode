from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mkdocs-pseudocode',
    version='0.1.2',
    description='A MkDocs plugin to render beautiful pseudocode with LaTeX-inspired syntax.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jules Topart',
    author_email='jules.topart@gmail.com',
    url='https://github.com/JulesTopart/mkdocs-pseudocode',
    packages=find_packages(),
    install_requires=[
        'mkdocs',
        'mkdocs-material',
    ],
    entry_points={
        'mkdocs.plugins': [
            'pseudocode = mkdocs_pseudocode_plugin.plugin:PseudocodePlugin',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
    license='MIT',
    include_package_data=True,
)

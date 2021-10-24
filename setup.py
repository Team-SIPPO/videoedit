from setuptools import setup, find_packages

install_requires = [
    # 必要な依存ライブラリがあれば記述
    "av>=8.0.3",
    "requests>=2.14.2",
]

packages = [
    'videoedit',
]

# console_scripts = [
#     'sample_lib_cli=sample_lib_cli.call:main',
# ]


setup(
    name='videoedit',
    version='0.0.0',
    packages=packages + find_packages(),
    install_requires=install_requires,
    # entry_points={'console_scripts': console_scripts},
)
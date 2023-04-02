from setuptools import setup, find_namespace_packages

setup(
      name='Bot-assistant',
      version='1.0.2',
      description='Sorts files, adds notes and contacts',
      long_description=open("README.md", encoding="utf-8").read(),
      url='https://github.com/InnaHub-dev/team-project.git',
      readme='README.md',
      python_requires=">=3.7",
      author='Inna Hubenko',
      author_email='learneng.ge@gmail.com',
      license='MIT',
      packages=find_namespace_packages(exclude=['newenv']),
      install_requires=[
          "color-it",
          "prompt-toolkit",
          "prettytable",
          ],
      include_package_data=True,
      entry_points={'console_scripts':['assist = bot_assistant.__main__:main']},
)

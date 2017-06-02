from setuptools import setup

setup(name='tyr_client',
      version='1.1',
      description='client for tyr server',
      url='',
      author='Nick Rosbrook',
      author_email='nrosbrook@mail.smcvt.edu',
      license='MIT',
      packages=['tyr_client'],
      entry_points = {
          'console_scripts': ['tyr_client=tyr_client.command_line:main'],
      },
      zip_safe=False)

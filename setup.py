from setuptools import find_packages, setup

__version__ = '0.2'

setup(
    name='ckanext-statistics',
    version=__version__,
    description='NHM Stats plugin.',
    long_description='',
    classifiers=[],
    keywords='',
    author='Natural History Museum',
    author_email='data@nhm.ac.uk',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'stats', 'tests']),
    namespace_packages=['ckanext', 'ckanext.statistics'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        """
            [ckan.plugins]
            statistics=ckanext.statistics.plugin:StatisticsPlugin
            [paste.paster_command]
            statistics=ckanext.statistics.commands.statistics:StatisticsCommand
        """,
    )

import setuptools

setuptools.setup(name="dockeraken",
                 packages=setuptools.find_packages(exclude=["test"]),
                 version="1.0.0",
                 author="Tuan Nguyen Minh",
                 author_email="tuana9a@gmail.com",
                 entry_points={
                     "console_scripts":
                     ["dockerakend=dockeraken.cmd.daemon:main"]
                 },
                 install_requires=["docker>=5.0.3", "pika>=1.2.0"])

from setuptools import setup
import jsoncls

jsoncls_classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

with open("README.md", "r") as fp:
    jsoncls_long_description = fp.read()

with open("requirements.txt", "r") as fp:
    requirements = fp.read()
requirements = requirements.strip().splitlines()

setup(name="jsoncls",
      version=jsoncls.__version__,
      author="NieXiaoyi",
      author_email="756102681@qq.com",
      url="https://github.com/NieXiaoyi/jsoncls",
      packages=["jsoncls"],
      install_requires=requirements,
      description="a library that supports both of python2 and python3, "
                  "can load a json as an object, and also can dump an object to a json",
      long_description=jsoncls_long_description,
      license="MIT",
      classifiers=jsoncls_classifiers,
      python_requires=">=2.7, >=3.7",
      )

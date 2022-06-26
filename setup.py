import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neurotraceutils",
    author="Peter Newstein",
    author_email="peternewstein@gmail.com",
    description="some tools for tracing neurons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnewstein/neurotraceutils",
    packages=["neurotraceutils"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"neurotraceutils": ["py.typed"]},
    python_requires='>=3.8',
    install_requires=["h5py", "pandas", "click", "numpy"]
)

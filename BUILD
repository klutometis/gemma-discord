load("@rules_python//python:pip.bzl", "compile_pip_requirements")
load("@pip//:requirements.bzl", "requirement")
load("@rules_python//python:py_binary.bzl", "py_binary")

package(default_visibility = ["//visibility:public"])

compile_pip_requirements(
    name = "requirements",
    src = "requirements.in",
    requirements_txt = "requirements.txt",
    visibility = ["//visibility:public"],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [
        requirement("discord"),
        requirement("langchain"),
        requirement("langchain-core"),
        requirement("langchain-google-vertexai"),
        requirement("pyparsing"),
    ],
    data = [":requirements", "params.json"],
)

py_binary(
    name = "llama",
    srcs = ["llama.py"],
    deps = [
    ],
    data = [":requirements", "params.json", ":bot"],
)

py_binary(
    name = "gemini",
    srcs = ["gemini.py"],
    deps = [
    ],
    data = [":requirements", "params.json", ":bot"],
)

py_library(name = "bot", srcs = ["bot.py"])

sh_binary(
    name = "run",
    srcs = ["run.sh"],
    data = [
        ":main",
        ":llama",
        ":gemini",
    ],
)

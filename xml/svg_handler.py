# svg_handler.py

from xml.sax.handler import ContentHandler
from xml.sax import parse


class SVGHandler(ContentHandler):

    def startElement(self, name, attrs):
        print(f"BEGIN: <{name}>, {attrs.keys()}")

    def endElement(self, name):
        print(f"END: </{name}>")

    def characters(self, content):
        if content.strip() != "":
            print("CONTENT:", repr(content))


def main():
    parse("smiley.svg", SVGHandler())

if __name__ == "__main__":
    main()

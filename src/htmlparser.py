#Represents the text in between tags
class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = [] #Text has no children but is present due to consistancy
        self.parent = parent
    
    #Method for printing the text
    def __repr__(self):
        return repr(self.text)

#Represents the tags of the HTML code
class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes #Some tags can have attributes like ids, classes...
        self.children = []
        self.parent = parent

    #Method for printing the tags
    def __repr__(self):
        return '<' + self.tag + '>'

#Represents the HTML parser
class HTMLParser:
    def __init__(self, body):
        self.body = body #HTML code
        self.unfinished = [] #Tags yet to be closed during parsing
        self.SELF_CLOSING_TAGS = [
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
            'input', 'link', 'meta', 'param', 'source', 'track',
            'wbr' 
        ]
        self.HEAD_TAGS = [
            'base', 'basefont', 'bgsound', 'noscript', 'link',
            'meta', 'title', 'style', 'script'
        ]

    #Logic behind parsing
    def parse(self):
        text = ''
        in_tag = False
        for c in self.body: #Read from body
            if c == '<': #If in an open tag
                in_tag = True 
                if text: self.add_text(text) #Add text element
                text = ''
            elif c == '>':
                in_tag = False
                self.add_tag(text) #Add node element
                text = ''
            else:
                text += c
        if not in_tag and text:
            self.add_text(text) #If at end and there's text, add text
        return self.finish() #Finish the parsing tree
    
    #Handle if some tags have been omitted
    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != 'html':
                self.add_tag('html')
            elif open_tags == ['html'] and tag not in \
            ['head', 'body', '/html']:
                if tag in self.HEAD_TAGS:
                    self.add_tag('head')
                else:
                    self.add_tag('body')
            elif open_tags == ['html', 'head'] and \
            tag not in ['/head'] + self.HEAD_TAGS:
                self.add_tag('/head')
            else:
                break

    def add_text(self, text):
        if text.isspace(): return
        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        tag, attributes = self.get_attributes(tag) #Get attributes of tags
        if tag.startswith('!'): return
        self.implicit_tags(tag) #Skip tag that start with !
        if tag.startswith('/'): #Handle finishing tags
            if len(self.unfinished) == 1: return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    #Method to finish the parse tree
    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished) > 1: #Finish all open tags if not finished
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node) #Append to all unfinished tags the last unfinished tag as child
        return self.unfinished.pop() #Return last tag
    
    #Get attributes by spliting the tag by spaces and store the key=value into a dictionary 
    def get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if '=' in attrpair:
                key, value = attrpair.split('=', 1)
                if len(value) > 2 and value[0] in ['\'', '"']:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else: #Handle attributes that don't need value like 'disabled'
                attributes[attrpair.casefold()] = ''
        return tag, attributes
    
    #Recursively print the tree
    def print_tree(self, node, indent=0):
        print(' ' * indent, node)
        for child in node.children:
            self.print_tree(child, indent + 2)
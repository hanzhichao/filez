def get_xml_children(node):
    children = list(node)
    if children:
        return [{'tag': node.tag,
                 'attrs': node.attrib,
                 'text': node.text.strip(),
                 'children': get_xml_children(child)
                 } for child in children]

    return {'tag': node.tag,
            'attrs': node.attrib,
            'text': node.text or None}


def parse_xml_node(node, ignore_attrs=False, attr_key_prefix=':', child_tag_key_prefix='', default_text_key='text',
                   empty_text=None):
    children = list(node)
    key = child_tag_key_prefix + node.tag
    text = node.text or empty_text
    node_data_value = {attr_key_prefix + k: v for k, v in node.attrib.items()} if not ignore_attrs and node.attrib else {}

    if not children:
        if ignore_attrs or not node.attrib:
            return {key: text}
        return {**node_data_value, default_text_key: text}

    for child in children:
        child_data = parse_xml_node(child, ignore_attrs=ignore_attrs, attr_key_prefix=attr_key_prefix,
                                    child_tag_key_prefix=child_tag_key_prefix, default_text_key=default_text_key,
                                    empty_text=empty_text)  # {key: {} } or {key: xxx}
        child_key = child_tag_key_prefix + child.tag
        child_value = child_data[child_key] if child_key in child_data.keys() else child_data
        if child_key in node_data_value.keys():
            child_value = child_data[child_key]
            node_data_value[child_key] = [node_data_value[child_key]]  # orgin
            node_data_value[child_key].append(child_value)
        else:
            node_data_value[child_key] = child_value
    return {key: node_data_value}


def parse_xml_node_ignore_attrs(node, empty_text=None):
    children = list(node)
    key = node.tag
    text = node.text or empty_text

    if not children:
        return {key: text}

    node_data_value = {}
    for child in children:
        child_data = parse_xml_node(child)  # {key: {} } or {key: xxx}
        child_key = child.tag
        child_value = child_data[child_key] if child_key in child_data.keys() else child_data
        if child_key in node_data_value.keys():
            child_value = child_data[child_key]
            node_data_value[child_key] = [node_data_value[child_key]]  # orgin
            node_data_value[child_key].append(child_value)
        else:
            node_data_value[child_key] = child_value
    return {key: node_data_value}

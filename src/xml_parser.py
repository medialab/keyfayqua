from lxml import etree
from constants import NS, CSVRow


def xml_to_row(sov: etree._Element, target: str | None) -> list | None:
    # Assume the tree has the target
    has_target = False

    # Reset data
    voice = None
    subject_lemma = None
    verb_lemma = None
    object_lemma = None

    # Find object and check for target
    obj = sov.find("obj", namespaces=NS)
    if obj is not None:
        object_lemma = obj.get("lemma")
        if target and target.lower() in object_lemma.lower():
            has_target = True

    # Find subject and do final check for target
    subj = sov.find("nsubj", namespaces=NS)
    if subj is not None:
        subject_lemma = subj.get("lemma")
        if "pass" in subj.get("dep"):
            voice = "passive"
        else:
            voice = "active"
        if target and target.lower() in subject_lemma.lower():
            has_target = True

    # If the target noun has been found, proceed parsing
    if (target and has_target) or not target:
        verb = sov.find("verb", namespaces=NS)
        if verb is not None:
            verb_lemma = verb.get("lemma")

        return CSVRow(
            **{
                "voice": voice,
                "subject_lemma": subject_lemma,
                "verb_lemma": verb_lemma,
                "object_lemma": object_lemma,
            }
        ).as_csv_row()


def build_dependency_tree(root) -> etree._Element:
    for sent in root.iter("sentence"):
        tokens = sent.find("tokens")
        dep_tree = etree.SubElement(sent, "dependeny_tree", attrib={}, nsmap=NS)

        # Get all subject-object-verb triples
        for verb in tokens.findall("token[@pos='VERB']"):
            triple = etree.SubElement(
                dep_tree, "subject-object-verb", attrib={}, nsmap=NS
            )
            etree.SubElement(triple, "verb", attrib=get_token_atts(verb), nsmap=NS)
            for child_attrib in get_children(parent_id=verb.get("id"), tokens=tokens):
                if child_attrib and child_attrib["dep"].startswith("nsubj"):
                    etree.SubElement(triple, "nsubj", attrib=child_attrib, nsmap=NS)
                elif child_attrib and child_attrib["dep"].startswith("obj"):
                    etree.SubElement(triple, "obj", attrib=child_attrib, nsmap=NS)
    return root


def get_token_atts(token):
    return {
        "id": token.get("id"),
        "head_id": token.get("head_id"),
        "dep": token.get("dep"),
        "text": token.get("text"),
        "lemma": token.get("lemma"),
        "tag": token.get("tag"),
        "pos": token.get("pos"),
    }


def get_children(parent_id, tokens):
    for token in tokens.findall(f"token[@head_id='{parent_id}']"):
        attribs = get_token_atts(token)
        if attribs["head_id"] != attribs["id"]:
            yield attribs

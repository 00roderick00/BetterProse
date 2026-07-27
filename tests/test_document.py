from betterprose.document import map_document


def test_document_maps_paragraphs_and_sentences() -> None:
    document = map_document("First sentence. Second sentence.\n\nAnother paragraph.")
    assert document.paragraphs[0].location == "P1"
    assert document.paragraphs[0].sentences[1].location == "P1.S2"
    assert document.paragraphs[1].location == "P2"
    assert document.stats.paragraphs == 2
    assert document.stats.sentences == 3


def test_numbered_text_preserves_locations() -> None:
    document = map_document("Alpha.\n\nBeta.")
    assert document.numbered_text() == "[P1] Alpha.\n\n[P2] Beta."

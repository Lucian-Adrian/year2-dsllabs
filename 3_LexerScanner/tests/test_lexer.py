import inspect

import pytest
from rich.text import Text
from src.highlighter import highlight_source
from src.lexer import LexicalError, TensorScriptLexer
from src.tokens import TokenType

SAMPLE_SOURCE = """// Define a neural network layer
let weights = [[0.5, -0.1], [sin(0.2), relu(0.9)]];
let bias = [1.0, 0.0];
"""


def collect_types(tokens):
    return [token.token_type for token in tokens]


class TestTensorScriptLexer:
    def test_tokenize_returns_generator(self):
        lexer = TensorScriptLexer(SAMPLE_SOURCE)
        stream = lexer.tokenize()
        assert inspect.isgenerator(stream)

    def test_sample_program_token_types(self):
        lexer = TensorScriptLexer(SAMPLE_SOURCE)
        tokens = lexer.collect()
        token_types = collect_types(tokens)

        assert TokenType.COMMENT in token_types
        assert token_types.count(TokenType.KEYWORD) == 2
        assert token_types.count(TokenType.MATH_FUNCTION) == 2
        assert token_types.count(TokenType.FLOAT) == 6
        assert token_types[-1] is TokenType.EOF

    def test_precise_line_and_column_tracking(self):
        lexer = TensorScriptLexer(SAMPLE_SOURCE)
        tokens = lexer.collect()
        weights = next(token for token in tokens if token.lexeme == "weights")
        relu = next(token for token in tokens if token.lexeme == "relu")
        bias = next(token for token in tokens if token.lexeme == "bias")

        assert (weights.line, weights.column) == (2, 5)
        assert (relu.line, relu.column) == (2, 40)
        assert (bias.line, bias.column) == (3, 5)

    def test_comments_can_be_suppressed(self):
        lexer = TensorScriptLexer(SAMPLE_SOURCE)
        lexer.config.emit_comments = False
        tokens = lexer.collect()
        assert TokenType.COMMENT not in collect_types(tokens)

    def test_malformed_number_raises_precise_diagnostic(self):
        source = "let broken = 1.2.3;"
        lexer = TensorScriptLexer(source)

        with pytest.raises(LexicalError) as error:
            list(lexer.tokenize())

        rendered = error.value.render()
        assert "Malformed numeric literal." in rendered
        assert "1.2." in rendered
        assert "^" in rendered

    def test_invalid_character_raises_precise_diagnostic(self):
        source = "let weights = @[0.5];"
        lexer = TensorScriptLexer(source)

        with pytest.raises(LexicalError) as error:
            list(lexer.tokenize())

        rendered = error.value.render()
        assert "Unrecognized token." in rendered
        assert "@" in rendered
        assert "Line 1, Column 15" in rendered

    def test_highlighter_preserves_original_text(self):
        lexer = TensorScriptLexer(SAMPLE_SOURCE)
        tokens = lexer.collect()
        highlighted = highlight_source(SAMPLE_SOURCE, tokens)

        assert isinstance(highlighted, Text)
        assert highlighted.plain == SAMPLE_SOURCE

    def test_integer_literals_are_supported(self):
        lexer = TensorScriptLexer("let units = [1, 2, 3];")
        tokens = lexer.collect()
        integers = [
            token.value for token in tokens if token.token_type is TokenType.INTEGER
        ]
        assert integers == [1, 2, 3]

    def test_softmax_is_lexed_as_math_function(self):
        lexer = TensorScriptLexer("let output = softmax(1.0);")
        tokens = lexer.collect()
        softmax = next(token for token in tokens if token.lexeme == "softmax")
        assert softmax.token_type is TokenType.MATH_FUNCTION

    def test_tokens_can_be_serialized_to_json(self):
        # verify that downstream dashboard logic (dumping tokens) will not break
        lexer = TensorScriptLexer("let a = 42;")
        tokens = lexer.collect()
        import json
        from dataclasses import asdict
        # use default=str for objects like SourceSpan
        json_text = json.dumps([asdict(t) for t in tokens], default=str)
        assert isinstance(json_text, str)

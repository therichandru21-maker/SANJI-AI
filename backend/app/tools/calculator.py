import ast
import operator


# ================================================================
# ALLOWED OPERATORS
# ================================================================

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


# ================================================================
# SAFE EVALUATOR
# ================================================================

def safe_evaluate(expression: str):
    """
    Safely evaluate a mathematical expression using AST.

    Only basic mathematical operators are allowed.
    Arbitrary Python code cannot be executed.
    """

    try:
        tree = ast.parse(
            expression,
            mode="eval"
        )

    except SyntaxError:
        raise ValueError("Invalid mathematical expression.")

    return evaluate_node(tree.body)


def evaluate_node(node):
    """
    Recursively evaluate allowed AST nodes.
    """

    # Numbers
    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):

            return node.value

        raise ValueError("Only numbers are allowed.")

    # Unary operators: -5, +5
    if isinstance(node, ast.UnaryOp):

        operator_function = ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if operator_function is None:
            raise ValueError("Unsupported operator.")

        return operator_function(
            evaluate_node(node.operand)
        )

    # Binary operators: +, -, *, /, %, **
    if isinstance(node, ast.BinOp):

        operator_function = ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if operator_function is None:
            raise ValueError("Unsupported operator.")

        left = evaluate_node(node.left)
        right = evaluate_node(node.right)

        # Prevent extremely large exponent calculations
        if isinstance(node.op, ast.Pow):

            if abs(right) > 100:
                raise ValueError(
                    "Exponent is too large."
                )

        return operator_function(
            left,
            right
        )

    raise ValueError(
        "Expression contains unsupported operations."
    )


# ================================================================
# CALCULATOR TOOL
# ================================================================

def calculator(expression: str) -> dict:
    """
    SANJI AI calculator tool.

    Supports:
    +   Addition
    -   Subtraction
    *   Multiplication
    /   Division
    %   Modulus
    **  Power
    """

    if not expression or not expression.strip():

        return {
            "success": False,
            "error": "Expression cannot be empty."
        }

    expression = expression.strip()

    # Basic length protection
    if len(expression) > 200:

        return {
            "success": False,
            "error": "Expression is too long."
        }

    try:

        result = safe_evaluate(expression)

        return {
            "success": True,
            "expression": expression,
            "result": result
        }

    except ZeroDivisionError:

        return {
            "success": False,
            "expression": expression,
            "error": "Division by zero is not allowed."
        }

    except ValueError as e:

        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }

    except Exception as e:

        return {
            "success": False,
            "expression": expression,
            "error": f"Calculation failed: {str(e)}"
        }
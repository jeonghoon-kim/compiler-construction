import ply.yacc as yacc
import decaflexer
import sys
import logging

from decaflexer import tokens
#from decaflexer import errorflag
from decaflexer import lex

from ast import *


precedence = (
    ('right', 'ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LEQ', 'GEQ', 'LT', 'GT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
    ('right', 'ELSE'),
    ('right', 'RPAREN'),
)

class count:
    const_cnt = 0
    method_cnt = 0
    field_cnt = 0

def init():
    decaflexer.errorflag = False
    
### DECAF Grammar

# Top-level
def p_pgm(p):
    'pgm : class_decl_list'
    p[0] = PGM(p[1])

def p_class_decl_list_nonempty(p):
    'class_decl_list : class_decl class_decl_list'
    p[0] = CLASS_DECL_LIST(p[1], p[2])

def p_class_decl_list_empty(p):
    'class_decl_list : '
    p[0] = CLASS_DECL_LIST(None, None)

def p_class_decl(p):
    'class_decl : CLASS ID extends LBRACE class_body_decl_list RBRACE'
    p[0] = CLASS_DECL(p[2], p[3], p[5])

def p_class_decl_error(p):
    'class_decl : CLASS ID extends LBRACE error RBRACE'
    # error in class declaration; skip to next class decl.
    pass

def p_extends_id(p):
    'extends : EXTENDS ID '
    p[0] = EXTENDS_ID(p[2])
    
def p_extends_empty(p):
    'extends : '
    pass

def p_class_body_decl_list_plus(p):
    'class_body_decl_list : class_body_decl_list class_body_decl'
    p[0] = CLASS_BODY_DECL_LIST(p[1], p[2])

def p_class_body_decl_list_single(p):
    'class_body_decl_list : class_body_decl'
    p[0] = CLASS_BODY_DECL_LIST(None, p[1])

def p_class_body_decl_field(p):
    'class_body_decl : field_decl'
    p[0] = CLASS_BODY_DECL_FIELD(p[1])

def p_class_body_decl_method(p):
    'class_body_decl : method_decl'
    p[0] = CLASS_BODY_DECL_METHOD(p[1])

def p_class_body_decl_constructor(p):
    'class_body_decl : constructor_decl'
    p[0] = CLASS_BODY_DECL_CONSTRUCTOR(p[1])

# Field/Method/Constructor Declarations

def p_field_decl(p):
    'field_decl : mod var_decl'
    count.field_cnt += 1
    p[0] = FIELD_DECL(count.field_cnt, p[1], p[2])

def p_method_decl_void(p):
    'method_decl : mod VOID ID LPAREN param_list_opt RPAREN block'
    count.method_cnt += 1
    p[0] = METHOD_DECL(count.method_cnt, p[1], p[2], p[3], p[5], p[7])

def p_method_decl_nonvoid(p):
    'method_decl : mod type ID LPAREN param_list_opt RPAREN block'
    count.method_cnt += 1
    p[0] = METHOD_DECL(count.method_cnt, p[1], p[2], p[3], p[5], p[7])

def p_constructor_decl(p):
    'constructor_decl : mod ID LPAREN param_list_opt RPAREN block'
    count.const_cnt += 1
    p[0] = CONSTRUCTOR_DECL(count.const_cnt, p[1], p[4], p[6])
    
def p_mod(p):
    'mod : visibility_mod storage_mod'
    p[0] = MOD(p[1], p[2])

def p_visibility_mod_pub(p):
    'visibility_mod : PUBLIC'
    p[0] = VISIBILITY_MOD(p[1])

def p_visibility_mod_priv(p):
    'visibility_mod : PRIVATE'
    p[0] = VISIBILITY_MOD(p[1])

def p_visibility_mod_empty(p):
    'visibility_mod : '
    p[0] = VISIBILITY_MOD(None)

def p_storage_mod_static(p):
    'storage_mod : STATIC'
    p[0] = STORAGE_MOD(p[1])

def p_storage_mod_empty(p):
    'storage_mod : '
    p[0] = STORAGE_MOD(None)

def p_var_decl(p):
    'var_decl : type var_list SEMICOLON'
    p[0] = VAR_DECL(p[1], p[2])

def p_type_int(p):
    'type :  INT'
    p[0] = TYPE(p[1])
    #pass
def p_type_bool(p):
    'type :  BOOLEAN'
    p[0] = TYPE(p[1])
    #pass
def p_type_float(p):
    'type :  FLOAT'
    p[0] = TYPE(p[1])
    #pass
def p_type_id(p):
    'type :  ID'
    p[0] = TYPE(p[1])

def p_var_list_plus(p):
    'var_list : var_list COMMA var'
    p[0] = VAR_LIST(p[1], p[3])

def p_var_list_single(p):
    'var_list : var'
    p[0] = VAR_LIST(None, p[1])

def p_var_id(p):
    'var : ID'
    p[0] = VAR(p[1])

def p_var_array(p):
    'var : var LBRACKET RBRACKET'
    p[0] = p[1]

def p_param_list_opt(p):
    'param_list_opt : param_list'
    p[0] = PARAM_LIST_OPT(p[1])
    pass
def p_param_list_empty(p):
    'param_list_opt : '
    pass

def p_param_list(p):
    'param_list : param_list COMMA param'
    p[0] = PARAM_LIST(p[1], p[3])

def p_param_list_single(p):
    'param_list : param'
    p[0] = PARAM_LIST(None, p[1])

def p_param(p):
    'param : type ID'
    p[0] = PARAM(p[1], p[2])

# Statements

def p_block(p):
    'block : LBRACE stmt_list RBRACE'
    p[0] = BLOCK(p[2])

def p_block_error(p):
    'block : LBRACE stmt_list error RBRACE'
    # error within a block; skip to enclosing block
    pass

def p_stmt_list_empty(p):
    'stmt_list : '
    p[0] = STMT_LIST(None, None)

def p_stmt_list(p):
    'stmt_list : stmt_list stmt'
    p[0] = STMT_LIST(p[1], p[2])

def p_stmt_if(p):
    '''stmt : IF LPAREN expr RPAREN stmt ELSE stmt
          | IF LPAREN expr RPAREN stmt'''
    if(len(p) == 8):
        p[0] = STMT_IF(p[1], p[3], p[5], p[6], p[7])
    else:
        p[0] = STMT_IF(p[1], p[3], p[5], None, None)

def p_stmt_while(p):
    'stmt : WHILE LPAREN expr RPAREN stmt'
    p[0] = STMT_WHILE(p[1], p[3], p[5])

def p_stmt_for(p):
    'stmt : FOR LPAREN stmt_expr_opt SEMICOLON expr_opt SEMICOLON stmt_expr_opt RPAREN stmt'
    p[0] = STMT_FOR(p[1], p[3], p[5], p[7], p[9])

def p_stmt_return(p):
    'stmt : RETURN expr_opt SEMICOLON'
    p[0] = STMT_RETURN(p[1], p[2])

def p_stmt_stmt_expr(p):
    'stmt : stmt_expr SEMICOLON'
    p[0] = STMT_STMT_EXPR(p[1])
    #pass
def p_stmt_break(p):
    'stmt : BREAK SEMICOLON'
    p[0] = STMT_BREAK(p[1])

def p_stmt_continue(p):
    'stmt : CONTINUE SEMICOLON'
    p[0] = STMT_CONTINUE(p[1])

def p_stmt_block(p):
    'stmt : block'
    p[0] = STMT_BLOCK(p[1])

def p_stmt_var_decl(p):
    'stmt : var_decl'
    p[0] = STMT_VAR_DECL(p[1])

def p_stmt_error(p):
    'stmt : error SEMICOLON'
    print("Invalid statement near line {}".format(p.lineno(1)))
    decaflexer.errorflag = True

# Expressions
def p_literal_int_const(p):
    'literal : INT_CONST'
    p[0] = LITERAL_INT_CONST(p[1])

def p_literal_float_const(p):
    'literal : FLOAT_CONST'
    p[0] = LITERAL_FLOAT_CONST(p[1])

def p_literal_string_const(p):
    'literal : STRING_CONST'
    p[0] = LITERAL_STRING_CONST(p[1])

def p_literal_null(p):
    'literal : NULL'
    p[0] = LITERAL_NULL(p[1])

def p_literal_true(p):
    'literal : TRUE'
    p[0] = LITERAL_TRUE(p[1])

def p_literal_false(p):
    'literal : FALSE'
    p[0] = LITERAL_FALSE(p[1])

def p_primary_literal(p):
    'primary : literal'
    p[0] = PRIMARY_LITERAL(p[1])

def p_primary_this(p):
    'primary : THIS'
    p[0] = PRIMARY_THIS(p[1])

def p_primary_super(p):
    'primary : SUPER'
    p[0] = PRIMARY_SUPER(p[1])

def p_primary_paren(p):
    'primary : LPAREN expr RPAREN'
    p[0] = PRIMARY_LITERAL(p[1])

def p_primary_newobj(p):
    'primary : NEW ID LPAREN args_opt RPAREN'
    p[0] = PRIMARY_NEWOBJ(p[2], p[4])

def p_primary_lhs(p):
    'primary : lhs'
    p[0] = PRIMARY_LHS(p[1])

def p_primary_method_invocation(p):
    'primary : method_invocation'
    p[0] = PRIMARY_METHOD_INVOCATION(p[1])

def p_args_opt_nonempty(p):
    'args_opt : arg_plus'
    p[0] = ARGS_OPT(p[1])

def p_args_opt_empty(p):
    'args_opt : '
    p[0] = ARGS_OPT(None)

def p_args_plus(p):
    'arg_plus : arg_plus COMMA expr'
    p[0] = ARGS_PLUS(p[1], p[3])

def p_args_single(p):
    'arg_plus : expr'
    p[0] = ARGS_PLUS(None, p[1])

def p_lhs(p):
    '''lhs : field_access
           | array_access'''
    p[0] = LHS(p[1])

def p_field_access_dot(p):
    'field_access : primary DOT ID'
    p[0] = FIELD_ACCESS(p[1], p[3])

def p_field_access_id(p):
    'field_access : ID'
    p[0] = FIELD_ACCESS(None, p[1])

def p_array_access(p):
    'array_access : primary LBRACKET expr RBRACKET'
    p[0] = ARRAY_ACCESS(p[1], p[3])

def p_method_invocation(p):
    'method_invocation : field_access LPAREN args_opt RPAREN'
    p[0] = METHOD_INVOCATION(p[1], p[3])

def p_expr_basic(p):
    '''expr : primary
            | assign
            | new_array'''
    p[0] = EXPR_BASIC(p[1])
    #pass
def p_expr_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr EQ expr
            | expr NEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr GT expr
            | expr GEQ expr
            | expr AND expr
            | expr OR expr
    '''
    p[0] = EXPR_BINOP(p[1], p[2], p[3])

def p_expr_unop(p):
    '''expr : PLUS expr %prec UMINUS
            | MINUS expr %prec UMINUS
            | NOT expr'''
    p[0] = EXPR_UNOP(p[1], p[2])

def p_assign_equals(p):
    'assign : lhs ASSIGN expr'
    p[0] = ASSIGN_EQUALS(p[1], p[3])

def p_assign_post_inc(p):
    'assign : lhs INC'
    p[0] = ASSIGN_POST_INC(p[1])

def p_assign_pre_inc(p):
    'assign : INC lhs'
    p[0] = ASSIGN_PRE_INC(p[2])

def p_assign_post_dec(p):
    'assign : lhs DEC'
    p[0] = ASSIGN_POST_DEC(p[1])

def p_assign_pre_dec(p):
    'assign : DEC lhs'
    p[0] = ASSIGN_PRE_DEC(p[2])
##### Arrya ANHE #####
def p_new_array(p):
    'new_array : NEW type dim_expr_plus dim_star'
    pass

def p_dim_expr_plus(p):
    'dim_expr_plus : dim_expr_plus dim_expr'
    pass
def p_dim_expr_single(p):
    'dim_expr_plus : dim_expr'
    pass

def p_dim_expr(p):
    'dim_expr : LBRACKET expr RBRACKET'
    pass

def p_dim_star(p):
    'dim_star : LBRACKET RBRACKET dim_star'
    pass
def p_dim_star_empty(p):
    'dim_star : '
    pass
########################
def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''
    p[0] = STMT_EXPR(p[1])

def p_stmt_expr_opt(p):
    'stmt_expr_opt : stmt_expr'
    p[0] = STMT_EXPR_OPT(p[1])

def p_stmt_expr_empty(p):
    'stmt_expr_opt : '
    p[0] = STMT_EXPR_OPT(None)

def p_expr_opt(p):
    'expr_opt : expr'
    p[0] = EXPR_OPT(p[1])

def p_expr_empty(p):
    'expr_opt : '
    p[0] = EXPR_OPT(None)


def p_error(p):
    if p is None:
        print ("Unexpected end-of-file")
    else:
        print ("Unexpected token '{0}' near line {1}".format(p.value, p.lineno))
    decaflexer.errorflag = True

parser = yacc.yacc()

def from_file(filename):
    try:
        with open(filename, "rU") as f:
            init()
            print parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=None)
        return not decaflexer.errorflag
    except IOError as e:
        print "I/O error: %s: %s" % (filename, e.strerror)


if __name__ == "__main__" :
    f = open(sys.argv[1], "r")
    logging.basicConfig(
            level=logging.CRITICAL,
    )
    log = logging.getLogger()
    res = parser.parse(f.read(), lexer=lex.lex(module=decaflexer), debug=log)

    if parser.errorok :
        print("Parse succeed")
    else:
        print("Parse failed")

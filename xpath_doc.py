from lxml import etree

#Reference
ref = "http://www.w3.org/TR/xpath20/"

#EBNF grammar
grammar = """
[1]    	XPath 	   ::=    	Expr
[2]    	Expr 	   ::=    	ExprSingle ("," ExprSingle)*
[3]    	ExprSingle 	   ::=    	ForExpr
| QuantifiedExpr
| IfExpr
| OrExpr
[4]    	ForExpr 	   ::=    	SimpleForClause "return" ExprSingle
[5]    	SimpleForClause 	   ::=    	"for" "$" VarName "in" ExprSingle ("," "$" VarName "in" ExprSingle)*
[6]    	QuantifiedExpr 	   ::=    	("some" | "every") "$" VarName "in" ExprSingle ("," "$" VarName "in" ExprSingle)* "satisfies" ExprSingle
[7]    	IfExpr 	   ::=    	"if" "(" Expr ")" "then" ExprSingle "else" ExprSingle
[8]    	OrExpr 	   ::=    	AndExpr ( "or" AndExpr )*
[9]    	AndExpr 	   ::=    	ComparisonExpr ( "and" ComparisonExpr )*
[10]    	ComparisonExpr 	   ::=    	RangeExpr ( (ValueComp
| GeneralComp
| NodeComp) RangeExpr )?
[11]    	RangeExpr 	   ::=    	AdditiveExpr ( "to" AdditiveExpr )?
[12]    	AdditiveExpr 	   ::=    	MultiplicativeExpr ( ("+" | "-") MultiplicativeExpr )*
[13]    	MultiplicativeExpr 	   ::=    	UnionExpr ( ("*" | "div" | "idiv" | "mod") UnionExpr )*
[14]    	UnionExpr 	   ::=    	IntersectExceptExpr ( ("union" | "|") IntersectExceptExpr )*
[15]    	IntersectExceptExpr 	   ::=    	InstanceofExpr ( ("intersect" | "except") InstanceofExpr )*
[16]    	InstanceofExpr 	   ::=    	TreatExpr ( "instance" "of" SequenceType )?
[17]    	TreatExpr 	   ::=    	CastableExpr ( "treat" "as" SequenceType )?
[18]    	CastableExpr 	   ::=    	CastExpr ( "castable" "as" SingleType )?
[19]    	CastExpr 	   ::=    	UnaryExpr ( "cast" "as" SingleType )?
[20]    	UnaryExpr 	   ::=    	("-" | "+")* ValueExpr
[21]    	ValueExpr 	   ::=    	PathExpr
[22]    	GeneralComp 	   ::=    	"=" | "!=" | "<" | "<=" | ">" | ">="
[23]    	ValueComp 	   ::=    	"eq" | "ne" | "lt" | "le" | "gt" | "ge"
[24]    	NodeComp 	   ::=    	"is" | "<<" | ">>"
[25]    	PathExpr 	   ::=    	("/" RelativePathExpr?)
| ("//" RelativePathExpr)
| RelativePathExpr 	/* xgs: leading-lone-slash */
[26]    	RelativePathExpr 	   ::=    	StepExpr (("/" | "//") StepExpr)*
[27]    	StepExpr 	   ::=    	FilterExpr | AxisStep
[28]    	AxisStep 	   ::=    	(ReverseStep | ForwardStep) PredicateList
[29]    	ForwardStep 	   ::=    	(ForwardAxis NodeTest) | AbbrevForwardStep
[30]    	ForwardAxis 	   ::=    	("child" "::")
| ("descendant" "::")
| ("attribute" "::")
| ("self" "::")
| ("descendant-or-self" "::")
| ("following-sibling" "::")
| ("following" "::")
| ("namespace" "::")
[31]    	AbbrevForwardStep 	   ::=    	"@"? NodeTest
[32]    	ReverseStep 	   ::=    	(ReverseAxis NodeTest) | AbbrevReverseStep
[33]    	ReverseAxis 	   ::=    	("parent" "::")
| ("ancestor" "::")
| ("preceding-sibling" "::")
| ("preceding" "::")
| ("ancestor-or-self" "::")
[34]    	AbbrevReverseStep 	   ::=    	".."
[35]    	NodeTest 	   ::=    	KindTest | NameTest
[36]    	NameTest 	   ::=    	QName | Wildcard
[37]    	Wildcard 	   ::=    	"*"
| (NCName ":" "*")
| ("*" ":" NCName) 	/* ws: explicit */
[38]    	FilterExpr 	   ::=    	PrimaryExpr PredicateList
[39]    	PredicateList 	   ::=    	Predicate*
[40]    	Predicate 	   ::=    	"[" Expr "]"
[41]    	PrimaryExpr 	   ::=    	Literal | VarRef | ParenthesizedExpr | ContextItemExpr | FunctionCall
[42]    	Literal 	   ::=    	NumericLiteral | StringLiteral
[43]    	NumericLiteral 	   ::=    	IntegerLiteral | DecimalLiteral | DoubleLiteral
[44]    	VarRef 	   ::=    	"$" VarName
[45]    	VarName 	   ::=    	QName
[46]    	ParenthesizedExpr 	   ::=    	"(" Expr? ")"
[47]    	ContextItemExpr 	   ::=    	"."
[48]    	FunctionCall 	   ::=    	QName "(" (ExprSingle ("," ExprSingle)*)? ")" 	/* xgs: reserved-function-names */
				/* gn: parens */
[49]    	SingleType 	   ::=    	AtomicType "?"?
[50]    	SequenceType 	   ::=    	("empty-sequence" "(" ")")
| (ItemType OccurrenceIndicator?)
[51]    	OccurrenceIndicator 	   ::=    	"?" | "*" | "+" 	/* xgs: occurrence-indicators */
[52]    	ItemType 	   ::=    	KindTest | ("item" "(" ")") | AtomicType
[53]    	AtomicType 	   ::=    	QName
[54]    	KindTest 	   ::=    	DocumentTest
| ElementTest
| AttributeTest
| SchemaElementTest
| SchemaAttributeTest
| PITest
| CommentTest
| TextTest
| AnyKindTest
[55]    	AnyKindTest 	   ::=    	"node" "(" ")"
[56]    	DocumentTest 	   ::=    	"document-node" "(" (ElementTest | SchemaElementTest)? ")"
[57]    	TextTest 	   ::=    	"text" "(" ")"
[58]    	CommentTest 	   ::=    	"comment" "(" ")"
[59]    	PITest 	   ::=    	"processing-instruction" "(" (NCName | StringLiteral)? ")"
[60]    	AttributeTest 	   ::=    	"attribute" "(" (AttribNameOrWildcard ("," TypeName)?)? ")"
[61]    	AttribNameOrWildcard 	   ::=    	AttributeName | "*"
[62]    	SchemaAttributeTest 	   ::=    	"schema-attribute" "(" AttributeDeclaration ")"
[63]    	AttributeDeclaration 	   ::=    	AttributeName
[64]    	ElementTest 	   ::=    	"element" "(" (ElementNameOrWildcard ("," TypeName "?"?)?)? ")"
[65]    	ElementNameOrWildcard 	   ::=    	ElementName | "*"
[66]    	SchemaElementTest 	   ::=    	"schema-element" "(" ElementDeclaration ")"
[67]    	ElementDeclaration 	   ::=    	ElementName
[68]    	AttributeName 	   ::=    	QName
[69]    	ElementName 	   ::=    	QName
[70]    	TypeName 	   ::=    	QName
"""


#Sample
t = etree.HTML(u"""
<html>
    <head>
        <title>Title</title>
    </head>
    </body> 
        <div> 
            <p></p>
        </div>
        <div class = 'itembox'>
            <ul class = 'itemlist'>
                <li id="item1">A</li> 
                <li id="item2">B</li>
                <li id="item3">C</li>
                <li id="item4">D</li>
            </ul>
        </div>
    </body>
</html>
"""
) 
 
#Example

#[li, li, li, li],  search  li
print t.xpath("//li") 

#[div, div],  path selector
print t.xpath("//body/div")

#select by attrib
print t.xpath("//body/div[@class = 'itembox']")

#node has a class attrib
print t.xpath("//body/div/@class"]



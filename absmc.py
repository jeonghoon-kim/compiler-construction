import ast
import sys
import logging

static_data_size = 0
classtable = {}
lastlabel = 0

def find_static_var(classname, varname):
    for keys,values in staticdata.items():
        if values.inclass.name is classname and values.name is varname:
            print "STATIC %s (%s.%s)" % (keys, values.inclass.name, values.name)
            return values
    print "Not found"
    return None

def print_code(out, ct):
    global lastlabel
    global tmpreg, argreg, controlstack, datastack
    global static_data_size, staticdata, classtable

    # File Output Source
    outfile = open(out, 'w')
    classtable = ct
    static_data_size = ast.static_data_size
    staticdata = ast.staticdata

    outfile.write(".static_data %d\n" % static_data_size)
    outfile.write("top:\n")

    # Print all things in the classtable
    for keys,values in classtable.items():
        # Print out the label
        if values.builtin:
            continue
        else:
            outfile.write("\nC%d:\n" % lastlabel)
            lastlabel += 1
            if values.constructors:
                for constructor in values.constructors:
                    generate_code(constructor.body, outfile)
            if values.methods:
                for method in values.methods:
                    outfile.write("%s:\n" % method)
                    generate_code(method.body, outfile)
        """    for key,values in ast.treg.items():
                if key is not None:
                    print "Key:{0}\nValue:{1}".format(key.name, values)

                    for value in values:
                        print "value: {0}".format(value.name)"""

    outfile.write("\n__main__:\n")
    outfile.write("\tcall top\n")
    outfile.write("\tret")

    return None

def generate_code(body, outfile):
    global lastlabel

    if body.lines != None:
        for stmt in body.stmtlist:
            if stmt.type == "Skip":
                pass
            elif stmt.type == "Expr":
                l = "\t%s" % stmt.expr.codegen()
                outfile.write("%s\n"%l)
            elif stmt.type == "For":
                l = "%s" % stmt.codegen()
                outfile.write("%s"%l)
            elif stmt.type == "While":
                outfile.write("%s"%stmt.codegen())
            elif stmt.type == "If":
                outfile.write("\t%s"%stmt.codegen())
            elif stmt.type == "Continue":
                outfile.write("%s"%stmt.codegen())
            elif stmt.type == "Break":
                outfile.write("%s"%stmt.codegen())
            elif stmt.type == "Return":
                outfile.write("\t%s"%stmt.codegen())
            else:
                outfile.write("\tret\n");
        return None

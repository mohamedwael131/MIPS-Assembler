import os
register_map = {0:["$zero","$0"],1:["$at","$1"],2:["$v0","$2"],3:["$v1","$3"],4:["$a0","$4"],5:["$a1","$5"],6:["$a2","$6"],7:["$a3","$7"],8:["$t0","$8"]
                ,9:["$t1","$9"],10:["$t2","$10"],11:["$t3","$11"],12:["$t4","$12"],13:["$t5","$13"],14:["$t6","$14"],15:["$t7","$15"],16:["$s0","$16"]
                ,17:["$s1","$17"],18:["$s2","$18"],19:["$s3","$19"],20:["$s4","$20"],21:["$s5","$21"],22:["$s6","$22"],23:["$s7","$23"]
                ,24:["$t8","$24"],25:["$t9","$25"],26:["$k0","$26"],27:["$k1","$27"],28:["$gp","$28"],29:["$sp","$29"],30:["$fp","$30"],31:["$ra","$31"]}

def format_data(data,dist):
    ls_new = []
    ls = data.split("\n")
    if (ls[0] == "b") :
        for a in ls[1:]:
            formatted = bin_to_hex(a.strip().zfill(32))
            ls_new.append(formatted)
    elif(ls[0] == "h") :
        for a in ls[1:]:
            formatted = a.strip().zfill(8)
            ls_new.append(formatted)
    with open(dist,"w") as my:
        for a in ls_new:
            my.write(a+"\n") 



def get_content_unmodified(filename):
    with open(filename,"r") as my:
        content = my.read()
    return content.lower()


def get_program(name):
    with open(name,"r") as my:
        program = my.read().strip() ;
    return (program)

def correct_label(program,ls_sub):
    new = ""
    for a in ls_sub :
        new = program[0:a] + program[a+1:]
    return new
def remove_spaces(program):
    program = program.lower()
    ls = program.split("\n")
    ls_new =[]
    new_program =""
    for line in ls:
        count = 0
        line = line.strip()
        new_line =""
        for char in line :
            if ((char == " " and count == 0)):
                new_line= new_line + char
                count = count + 1
            elif(char != " "):
                new_line = new_line + char
        ls_new.append(new_line)
        new_program = new_program + new_line + ";"
    count = 0
    fuck = ""
    while(count < len(new_program)):
        try :
            if((new_program[count] == ";" and new_program[count-1] == ":")):
                count = count + 1
                continue
            else:
                fuck = fuck + new_program[count]
            count = count + 1
        except:
            count = count + 1
    ls_program = fuck.split(";")
    ls_jumps = {}
    ls_new_program = []
    for line in ls_program :
        for a in line :
            if (a == ":"):
                ls_jumps[ls_program.index(line)] = line[0:line.index(a)].strip()
                pos = line.index(a) + 1
                break
            else:
                pos = 0
        if (line == "" or line == " "):
            continue
        else:
            ls_new_program.append(line[pos:]) 
    return (ls_new_program,ls_jumps)
                    
formats = {0:["add","sub","slt","nor","or","and"],1:["addi","slti","ori","andi"],2:["lw","sw"],3:["lui"],4:["jal","j"],5:["jr"],6:["beq","bne"],7:["sll","sra","srl"]}
#format0     add,sub,slt,nor,or,and
#format1    addi , slti, ori, andi
#format2    lw , sw
#format3    lui
#forma4    jal j
#format5   jr
#format6  beq ,bne
#format7  sll,sra,srl


def pre_control(program):
    ls_formats = []
    for instruction in program:
        print(instruction)
        command = instruction.split(" ")[0]
        operators = instruction.split(" ")[1]
        for format_num in formats:
            for comm in formats[format_num]:
                if (comm == command):
                    ls_formats.append(format_num)
    return (ls_formats)




def control(ls_formats,ls_commands,ls_jumps):
    pc = 0
    ls = []
    while (pc < len(ls_formats)):
        format_ = ls_formats[pc]
        instruction = ls_commands[pc]
        if (format_ == 0):
            ls.append(format_0_mapping(instruction))
        elif (format_ == 1):
            ls.append(format_1_mapping(instruction))
        elif (format_ == 3):
            ls.append(format_3_mapping(instruction))
        elif (format_ == 5):
            ls.append(format_5_mapping(instruction))
        elif (format_==7):
            ls.append(format_7_mapping(instruction))
        elif (format_==2):
            ls.append(format_2_mapping(instruction))
        elif (format_== 4):
            ls.append(format_4_mapping(instruction,ls_jumps))
        elif (format_ == 6):
            ls.append(format_6_mapping(instruction,pc,ls_jumps))
        pc = pc + 1
        print(ls)
    return (ls)


format_0_list = {"add":32,"sub":34,"and":36,"nor":39,"or":37,"slt":42} #function bc all op is 0 
format_1_list = {"addi":8,"andi":12,"ori":13,"slti":10} #opcodes
format_7_list = {"sll":0,"srl":2,"sra":3}
#format (3,5,6,2,4) omitted 1/2 commands each


def format_4_mapping(instruction,jumps):
    command = instruction.split(" ")[0]
    j_add = instruction.split(" ")[1]
    if (command == "j"):
        opcode = write_bin(2,6)
    else :
        opcode = write_bin(3,6)
    if (int(translate_address(j_add,1,0,jumps)) == -1):
        j_add = 'X'*26
    else:
        j_add = write_bin(int(translate_address(j_add,1,0,jumps)),26)
    return (opcode+j_add)

        
def format_2_mapping(instruction): #negative
    command = instruction.split(" ")[0]
    operators = instruction.split(" ")[1].split(",")
    rt = write_bin(translate_regs(operators[0]),5)
    I_data = write_bin(int(operators[1].split("(")[0]),16)
    rs = write_bin(translate_regs(operators[1].split("(")[1].replace(")","")),5)
    if (command == "lw"):
        op_code = write_bin(35,6)
    else :
        op_code = write_bin(43,6)
    return (op_code+rs+rt+I_data)




def format_5_mapping(instruction): #checked
    rs = write_bin(translate_regs(instruction.split(" ")[1]),5)
    op_code = write_bin(0,6)
    rd = rt = shamt = write_bin(0,5)
    function = write_bin(8,6)
    return (op_code+rs+rt+rd+shamt+function)




def format_7_mapping(instruction): #checked
    command = instruction.split(" ")[0]
    operators = instruction.split(" ")[1].split(",")
    rd = write_bin(translate_regs(operators[0]),5)
    rt = write_bin(translate_regs(operators[1]),5)
    rs = write_bin(0,5)
    shamt = write_bin(int(operators[2]),5)
    op_code = write_bin(0,6)
    for a in format_7_list :
        if (command == a):
            function  = write_bin(format_7_list[a],6)
    return (op_code+rs+rt+rd+shamt+function)




def format_3_mapping(instruction): #checked #negative
    operators = instruction.split(" ")[1].split(",")
    I_data = write_bin(int(operators[1]),16)
    rt = write_bin(translate_regs(operators[0]),5)
    rs = write_bin(0,5)
    op_code = write_bin(15,6)
    return (op_code+rs+rt+I_data)




def format_0_mapping(instruction): #checked
    command = instruction.split(" ")[0]
    operators = instruction.split(" ")[1].split(",")
    rd = write_bin(translate_regs(operators[0]),5)
    rt = write_bin(translate_regs(operators[2]),5)
    rs = write_bin(translate_regs(operators[1]),5)
    shamt = write_bin(0,5)
    for a in format_0_list :
        if (a == command):
            function = format_0_list[a]
    function = write_bin(function,6)
    op_code = write_bin(0,6)
    return (op_code+rs+rt+rd+shamt+function)




def format_1_mapping(instruction): #checked #negative
    command = instruction.split(" ")[0]
    operators = instruction.split(" ")[1].split(",")
    rs = write_bin(translate_regs(operators[1]),5)
    rt = write_bin(translate_regs(operators[0]),5)
    I_data = write_bin(int(operators[2]),16)
    for op in format_1_list :
        if (op == command):
            op_code = write_bin(int(format_1_list[op]),6)
    return (op_code+rs+rt+I_data)



def translate_regs(reg):
    for regs in register_map :
        for b in register_map[regs]:
            if (reg == b):
                return regs

def translate_address(label , is_j , current_pos , jumps):
    for a in jumps :
        if (jumps[a] == label):
            if (is_j == 1):
                return a
            else :
                return (a-current_pos-1)
    return -1


def format_6_mapping(instruction,pc,jumps): #negative
    command = instruction.split(" ")[0]
    operators = instruction.split(" ")[1].split(",")
    rs = write_bin(translate_regs(operators[0]),5)
    rt = write_bin(translate_regs(operators[1]),5)
    branch_by = operators[2]
    if (command == "beq"):
            op_code = write_bin(4,6)
    else :
            op_code = write_bin(5,6)
    if (translate_address(branch_by,0,pc,jumps) != -1):
        branch_by = write_bin(int(translate_address(branch_by,0,pc,jumps)),16)
        return (op_code+rs+rt+branch_by)
    else :
        return (op_code+rs+rt+'X'*16)


            
    

def twoos_comp(number):
    count = 0
    new_number = ""
    number_rev = number[::-1]
    for a in number_rev :
        if (a == '1'):
            new_number = new_number + a
            start = count
            break
        count = count + 1
        new_number = new_number + a
    for a in number_rev[count+1:]:
        if (a == '1'):
            new_number = new_number + '0'
        else:
            new_number = new_number + '1'
    new_number = new_number[::-1]
    return (new_number)



def write_bin(number , size):
    if (number >= 0):
        return str(bin(number)).replace("0b","").zfill(size)
    else :
        number = number * -1
        number = str(bin(number)).zfill(size)
        return twoos_comp(str(number))



HEX_map = {'XXXX':'X','0000':'0','0001':'1','0010':'2','0011':'3','0100':'4','0101':'5','0110':'6','0111':'7','1000':'8','1001':'9','1010':'a','1011':'b','1100':'c','1101':'d','1110':'e','1111':'f'}


def bin_to_hex(number_32):
    count = 0
    HEXA = ""
    while (count < len(number_32)):
        digit = number_32[count:count+4]
        count = count + 4
        for a in HEX_map :
            if (a == digit):
                HEXA = HEXA + HEX_map[a]
    return HEXA

def format_mem(data,dist):
    ls_add = []
    lines = data.strip().split("\n")
    lines = lines[3:]
    to_print = ""
    for line in lines:
        new_line = line.strip()
        ls_add  = new_line.split(" ")
        for a in ls_add:
            if (a[::-1][0] != ":"):
                to_print = to_print + a + "\n"
    with open(dist,"w") as my:
        my.write(str(to_print))
    return (to_print)

def assemble(b):
    program = str(b)
    ready_program = remove_spaces(program)[0]
    ls_formats = pre_control(ready_program)
    jumps = remove_spaces(program)[1]
    returned = ""
    formatted_commands = control(ls_formats,ready_program,jumps)
    with open("program_file.txt","w") as my:
        for a in formatted_commands :
            my.write(bin_to_hex(a)+"\n")
            returned = returned + bin_to_hex(a) + "\n"
    return returned








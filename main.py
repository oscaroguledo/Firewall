import re, json, os

class Firewall():
    def __init__(self,command) -> None:
        self.rules=[]
        self.commands=["add","remove","list","help"]
        self.bounds=["-in","-out"]
        self.addresses=["10.0.0."+str(i) for i in range(256)]
        self.LETTERS = "abcdefghijklmnopqrstuvwxyz"
        self.numbers = "0123456789"
        self.symbols = "-. "
        self.added_rules=[]
        self.parsed_data=self.__parse_command(command)
    def __parse_command(self,cmd):
        res={"cmd":[],"rule":[],"bound":[],"addr":[]}
        data = []
        word=""
        for i in cmd:
            if i.lower() in self.LETTERS or i in self.symbols or i in self.numbers:
                if i == " ":
                    word = word.replace(" ","")
                    data.append(word)
                    word = ""
                word+=i
        
        for i in data:
            if len(i)==0:
                data.remove(i)
        
        ##getting command from command line
        for cmd in self.commands:
            if cmd in data:
                if len(res["cmd"]) <= 0 :
                    res["cmd"].append(cmd)
                    data.remove(cmd)
                else:
                    raise ValueError(f"\033[91mMultiple commands {res["cmd"][0]}{cmd} are not allowed \033[0m")
        
        if len(res["cmd"]) ==0:
            raise ValueError(f"\033[91mNO command was found. use any of {self.commands} \033[0m")

        ##getting rules from command line
        for i in data:
            try:
                if int(i) in self.rules:
                    if len(res["rule"]) <=0:
                        res["rule"].append(int(i))
                        data.remove(i)
                    else:
                        raise ValueError(f"\033[91mMultiple rules are not allowed \033[0m")
                else:
                    if len(res["rule"]) <=0:
                        self.rules.append(int(i))
                        res["rule"].append(int(i))
                        data.remove(i)
                    else:
                        raise ValueError(f"\033[91mMultiple rules are not allowed \033[0m")  
            except ValueError as err:
                pass
        
        if len(res["rule"]) ==0:
            if res["cmd"][0]=="Add" or res["cmd"][0]=="add":
                res["rule"].append(1)
            elif res["cmd"][0]=="List" or res["cmd"][0]=="list":
                pass
            elif res["cmd"][0]=="Help" or res["cmd"][0]=="help":
                pass
            else:
                raise ValueError(f"\033[91mPlease specify a rule \033[0m") 
        
        ##getting directions from command line
        for bound in self.bounds:
            if bound in data:
                if len(res["bound"]) <= 0 :
                    res["bound"].append(bound)
                    data.remove(bound)
                else:
                    raise ValueError(f"\033[91mMultiple directions {res["bound"][0]} {bound} are not allowed \033[0m")

        if len(res["bound"]) ==0:
            if res["cmd"][0]=="List" or res["cmd"][0]=="list":
                res["bound"]=[]
            else:
                res["bound"] = ["-in","-out"]
        
        ##getting addresses from command line
        for i in data:
            if "-" in i:
                i_list=i.split("-",1)#split only the first "-"
                if "." not in i_list[0][7:]:
                    st = abs(int(i_list[0][7:]))
                else:
                    raise ValueError(f"\033[91mInvalid IPv4 address {i_list[0][:7]+i_list[0][7:]} \033[0m")
                if "." not in i_list[-1][7:]:
                    end = abs(int(i_list[-1][7:]))
                else:
                    raise ValueError(f"\033[91mInvalid IPv4 address {i_list[-1][:7]+i_list[-1][7:]} \033[0m")
                
                i_list=["10.0.0."+str(i) for i in range(st,end+1)]
                for x in i_list:
                    if x in self.addresses:
                        res["addr"].append(x)
                    else:
                        raise ValueError(f"\033[91mInvalid IPv4 address {x} \033[0m")

            else:
                if i in self.addresses:
                    res["addr"].append(i)
                    data.remove(i)
                else:
                    print(i,"===", data)
                    raise ValueError(f"\033[91mInvalid IPv4 address {i} \033[0m")
        print("\033[93m"+str(res)+"\033[0m","\n")
        return res
    
    def __add_rule(self,parsed):
        print("\033[93mAdding rule...\033[0m")
        # Specify the file path
        file_path = "firewall_rules.json"
        # Update the existing data or add new key-value pairs
        data={}
        if "add" in parsed["cmd"] or "Add" in parsed["cmd"]:
            # Write data to the JSON file
            d={}
            for key,value in parsed.items():
                if len(value)==1:
                    d[key]= value[0]
                else:
                    d[key]= value
            data[int(d["rule"])]=d
        try:
            # Read existing data from the file
            with open(file_path, 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, start with an empty list
            existing_data = []

        # Append new data to the existing data
        if len(existing_data) ==0:
            existing_data.append(data)
        else:
            x =int(list(data.keys())[0])
            l=[int(list(i.keys())[0]) for i in existing_data]
            if x not in l:
                if len(existing_data) > x:
                    print('---///')
                    count= 0
                    for e in l:
                        if x< e:
                            existing_data.insert(count, data)
                            break
                        count+=1
                    
                    if count >= len(existing_data):
                        existing_data.append(data)
                elif len(existing_data) < x:
                    print('---+++')
                    count= 0
                    for e in l:
                        if x< e:
                            existing_data.insert(count, data)
                            break
                        count+=1
                elif len(existing_data) == x:
                    print('---==')
                    existing_data.append(data)
            else:
                print('---')
                existing_data.insert(l.index(x),data)

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(existing_data, file, indent=2)
        print("\033[93mRules added...\033[0m")
        return True
    
    def __remove_rule(self,parsed):
        print("\033[93mRemoving rule...\033[0m")
        # Specify the file path
        file_path = "firewall_rules.json"
        # Update the existing data or add new key-value pairs
        parsed_rule=str(parsed["rule"][0])
        try:
            # Read existing data from the file
            with open(file_path, 'r') as file:
                existing_data = json.load(file)

            for data in existing_data:
                if parsed_rule in data.keys():
                    if type(data[parsed_rule]["bound"]) == str:
                        if data[parsed_rule]["bound"] in parsed["bound"]:
                            existing_data.remove(data)

                    elif type(data[parsed_rule]["bound"]) == list:
                        if data[parsed_rule]["bound"] == parsed["bound"]:
                            print(parsed["bound"],"==",data[parsed_rule]["bound"], "===", data)
                            existing_data.remove(data)
                else:
                    raise ValueError(f"\033[91mNo rule {parsed_rule} exists, add a rule first. \033[0m")
            # Write the updated data back to the file
            with open(file_path, 'w') as file:
                json.dump(existing_data, file, indent=2)
            print("\033[93mRule removed...\033[0m")

        except FileNotFoundError:
            # If the file doesn't exist, start with an empty list
            raise ValueError(f"\033[91mNo rule exists, add a rule first. \033[0m")
    def __compute_addr(self,parsed, data):
        if type(list(data.values())[0]["addr"]) == str:
            if list(data.values())[0]["addr"] in parsed["addr"]:
                    self.added_rules.append(str(list(data.values())[0]))

            elif type(list(data.values())[0]["addr"]) == list:
                if list(data.values())[0]["addr"] == parsed["addr"]:
                    self.added_rules.append(str(list(data.values())[0]))
            else:
                self.added_rules.append(str(list(data.values())[0]))
    def __compute_in_addr(self,parsed, data):
        if len(parsed["addr"]) >0:
            if type(list(data.values())[0]["addr"]) == str:
                if list(data.values())[0]["addr"] in parsed["addr"]:
                    self.added_rules.append(str(list(data.values())[0]))

            elif type(list(data.values())[0]["addr"]) == list:
                if list(data.values())[0]["addr"] == parsed["addr"]:
                    self.added_rules.append(str(list(data.values())[0]))
            else:
                self.added_rules.append(str(list(data.values())[0]))
        else:
            self.added_rules.append(str(list(data.values())[0]))
    def __compute_in_bound(self,parsed, data):
        if type(list(data.values())[0]["bound"]) == str:
            if list(data.values())[0]["bound"] in parsed["bound"]:
                self.__compute_in_addr(parsed, data)

        elif type(list(data.values())[0]["bound"]) == list:
            if list(data.values())[0]["bound"] == parsed["bound"]:
                self.__compute_in_addr(parsed, data)
        else:
            self.added_rules.append(str(list(data.values())[0]))
    
    def __compute_in_rule(self,parsed, data):
        if str(parsed["rule"][0]) in data.keys():
            if len(parsed["bound"]) >0:
                self.__compute_in_bound(parsed, data)
            else:
                self.added_rules.append(str(list(data.values())[0]))
        else:
            pass

    def __list_rule(self,parsed):
        print("\033[93mFetching rules...\033[0m")
        # Specify the file path
        file_path = "firewall_rules.json"
        try:
            # Read existing data from the file
            with open(file_path, 'r') as file:
                existing_data = json.load(file)

            for data in existing_data:
                if len(parsed["rule"])>0:
                    self.__compute_in_rule(parsed, data)
                elif len(parsed["bound"])>0:
                    self.__compute_in_bound(parsed, data)
                elif len(parsed["addr"])>0:
                    self.__compute_addr(parsed, data)
                else:
                    self.added_rules.append(str(data))
            if len(self.added_rules)>0:
                [print(f"\033[92m{r}\033[0m") for r in set(self.added_rules)]
            else:
                print("\033[91mNO rule found. \033[0m")
            # Write the updated data back to the file
            with open(file_path, 'w') as file:
                json.dump(existing_data, file, indent=2)
            print("\033[93mDone fetching rules...\033[0m")

        except FileNotFoundError:
            raise ValueError(f"\033[91mNo rule exists, add a rule first. \033[0m")

    def __help(self,parse):
        display=str("\033[93marguments usage:\n"+
                    "help            How to use the package \n"+
                    "add [rule], [-in|-out] [addr or range or address]\t \033[94m e.g add 1 -in 10.0.0.5\033[0m\n"+
                    "\033[93mremove [rule], [-in|-out] [addr or range or address]\t \033[94m e.g remove 1 -in 10.0.0.5\033[0m\n"
                    "\033[93mlist [rule], [-in|-out] [addr or range or address]\t \033[94m e.g list 1 -in 10.0.0.5\033[0m  \033[0m\n")
        return display
    
    def run(self):
        if "add" in self.parsed_data["cmd"] or "Add" in self.parsed_data["cmd"]:
            self.__add_rule(self.parsed_data)
        elif "remove" in self.parsed_data["cmd"] or "Remove" in self.parsed_data["cmd"]:
            self.__remove_rule(self.parsed_data)
        elif "list" in self.parsed_data["cmd"] or "List" in self.parsed_data["cmd"]:
            self.__list_rule(self.parsed_data)
        else:
            help = self.__help(self.parsed_data)
            print(help)


if __name__ == "__main__":
    command =input()+" "
    firewall = Firewall(command)
    firewall.run()
    

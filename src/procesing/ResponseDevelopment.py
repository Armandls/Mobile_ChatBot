import pandas as pd
import nltk
import procesing.Converter as conv
import procesing.DfReader as reader

# Stop conversation words
byeWords = ["bye", "goodbye", "restart", "reset"]


class ResponseDevelopment:     
     
    def __init__(self, ui):
        # Reads from the dataset and gets ui.
        self.decision_dict = {}
        self.phones_df = reader.readDf()
        self.decision_df = pd.DataFrame()
        self.ui = ui
    
    def resetConversation(self):
        # Resets all conversation information and displays a bye message
        self.decision_dict = {}
        self.decision_df = pd.DataFrame()
        self.tokens = []
        self.ui.send_response("Bye! I hope I was able to help you find a mobile phone that fits your preferences. Now you can close the window or start a new conversation by asking me again.")
        
    def printSolution(self, df):
        # Check if there is at least one result after aplying all user filters
        if len(df) != 0:
            # Print all results
            self.ui.send_response(f"Here are the {len(df)} best phones that suit your preferences:")
            for i, (_, row) in enumerate(df.iterrows()):
                output = f"{i+1}. {row['name']}:\n\n"
                for col in reader.ResponseColumns:
                    output += f"\t- {reader.TranslateColumns[col]}: {row[col]} {reader.ResponseUnits[col]}\n"
                output += "\n"
                self.ui.display_phone(output, row["image"])
        else:
            self.ui.send_response("No phones were found given your specifications, please try to reset conversation and change your specifications.")
        
        

    def tryToAnswer(self):
        # Check if at least one filter was applied
        if len(self.decision_dict) != 0:
            # Make a copy of the original dataframe
            self.decision_df = self.phones_df.copy()
            
            # Filter the dataframe with the decision_dict
            for column, value in self.decision_dict.items():
                # Check if column is numeric
                if column in reader.ColumnsNumeric:
                    # Check if more, less, about or no modifier was applied and filter dataframe
                    if '+' in value:
                        new_value = float(value.replace('+', ''))
                        self.decision_df = self.decision_df[self.decision_df[column] > new_value]
                    elif '-' in value:
                        new_value = float(value.replace('-', ''))
                        self.decision_df = self.decision_df[self.decision_df[column] < new_value]
                    elif '~' in value:
                        new_value = float(value.replace('~', ''))
                        upper_value = new_value * 1.1
                        lower_value = new_value * 0.9
                        self.decision_df = self.decision_df[(self.decision_df[column] <= upper_value) & (self.decision_df[column] >= lower_value)]
                    else:
                        new_value = float(value)
                        self.decision_df = self.decision_df[self.decision_df[column] == new_value]
                # Check if column is brand and and filter dataframe
                elif column == "brand":
                    for brand in value:
                        if "-no-" in brand:
                            brand = brand.replace("-no-", "")
                            self.decision_df = self.decision_df[~self.decision_df["brand"].str.lower().str.contains(brand)]
                        else:
                            self.decision_df = self.decision_df[self.decision_df["brand"].str.lower().str.contains(brand)]
                # Check if column is os and and filter dataframe                
                elif column == "operating_system":
                    if "-no-" in value:
                        value = value.replace("-no-", "")
                        self.decision_df = self.decision_df[~self.decision_df["operating_system"].str.lower().str.contains(value)]
                    else:
                        self.decision_df = self.decision_df[self.decision_df["operating_system"].str.lower().str.contains(value)]
                elif column == "generation":
                    if "-no-" in value:
                        value = value.replace("-no-", "")
                        self.decision_df = self.decision_df[~self.decision_df["generation"].str.lower().str.contains(value)]
                    else:
                        self.decision_df = self.decision_df[self.decision_df["generation"].str.lower().str.contains(value)]
            # Check if too many results were gviven
            if len(self.decision_df) <= 10:
                self.printSolution(self.decision_df.sort_values(by = "price_euro", ascending = True))
            else:
                self.ui.send_response(f"I found too many matches with your specifications ({len(self.decision_df)} phones). Please add more specifications so I can reduce the amount of results.")
        else:
            self.ui.send_response(f"Please add at least one useful information so I can help you")
   
            
    def addDecisionInfo(self, units = None, value = None, column = None, spec = ""):
        # Check if units were given (value too)
        if units != None:  
            # Check if resolution of style <x_resol>x<y_resol> was given
            if units in conv.PxUnits:
                pixels = value.split("x")
                self.decision_dict["resolution_x"] = str(conv.unitsToStandard(units, float(pixels[0])))
                self.decision_dict["resolution_y"] = str(conv.unitsToStandard(units, float(pixels[1])))
            else:
                self.decision_dict[column] = str(conv.unitsToStandard(units, float(value))) + spec
        # Check if no units were given (qualitative word)
        elif value != None:
            self.decision_dict[column] = str(conv.adjAdvToStandard(value, column))
        # Error occured
        else:
            self.ui.send_response(f"\tGeneral error of {value} {column}")
            
    
    def checkForCompoundColumnName(self, prev_token, token, column):
        # Avoid reading 2 tokens as different if they belong to the same topic
        return prev_token in column and token in column
    
    def searchForQuantity(self, token, column):
        # Get index of current token
        token_index = self.tokens.index(token)     
        # Check if there is another word before this token 
        if token_index != 0:
            # Get previous token
            prev_token = self.tokens[token_index - 1]
            # Check if units are specified
            if prev_token in conv.Units:
                # Check if there is another previous word 
                if token_index > 1:
                    # Get previous token of previous token
                    possible_number = self.tokens[token_index - 2]
                    # Check if number is specified for this units
                    if possible_number in self.categories_dict["number"]:
                        # Check if "more", "less" or "about" is specified
                        spec = ""
                        if token_index > 2:
                            specifier = self.tokens[token_index - 3]
                            if specifier == "more":
                                spec = "+"
                            elif specifier == "less":
                                spec = "-"
                            elif specifier == "about" or specifier == "like" or specifier == "around":
                                spec = "~"
                        self.addDecisionInfo(units = prev_token, value = possible_number.replace(',' , '.'), column = column, spec = spec)
                    else:
                        # Only units were specified
                        self.ui.send_response(f"\tNo value for {prev_token} specified!")
            # Check if quantifier is specified (adjective or adverb)
            else: 
                # If there is a quantifier check that quantifier does not belong to compound column name
                if not self.checkForCompoundColumnName(prev_token, token, column):  
                    self.addDecisionInfo(value = prev_token, column = column)
                    
    def searchNot(self, token):
        # Get index of current token
        token_index = self.tokens.index(token)     
        # Check if there is another word before this token 
        if token_index != 0:
            # Get previous token
            prev_token = self.tokens[token_index - 1]
            if prev_token == "no" or prev_token == "without" or prev_token == "not":
                return "-no-" + token
        return token
            
    def getColumnByUnits(self, units):
        # Check if units are ambiguouss
        if units in conv.SizeUnits:
            self.ui.send_response(f"I haven't understood what the units {units} refer to, please specify which parameter they are referring to.")
            return None
        else:
            return conv.getColumnsByUnits(units)
            
            
    def searchForAloneUnits(self, units):
        # Get index of current token
        token_index = self.tokens.index(units)
        # Check if there is another word before this token 
        if token_index != 0:
            # Get previous token and check if is a number
            possible_number = self.tokens[token_index - 1]
            if possible_number in self.categories_dict["number"]:
                # Check if is not at the end of tokens
                if token_index != len(self.tokens) - 1:
                    # Get a possible paramater name and discard this token if True
                    post_token = self.tokens[token_index + 1]
                    for column in reader.Columns:
                        if post_token in column:
                            return
                        
                # Get column of the specified units
                column = self.getColumnByUnits(units)
                if column != None:
                    # Check if "more", "less" or "about" is specified
                    spec = ""
                    if token_index > 1:
                        specifier = self.tokens[token_index - 2]
                        # Check which specifier and mark value
                        if specifier == "more":
                            spec = "+"
                        elif specifier == "less":
                            spec = "-"
                        elif specifier == "about" or specifier == "like" or specifier == "around":
                            spec = "~"
                    # If all is correct add filter to decision dictionary
                    self.addDecisionInfo(units = units, value = possible_number.replace(',' , '.'), column = column, spec = spec)
 
          
    def developResponse(self, tokens):
        # Check if a stop conversation word is in tokens
        for word in byeWords:
            if word in tokens:
                self.resetConversation()
                self.ui.saveContext(self.decision_dict)
                return
        
        self.tokens = tokens
        
        # POS tagging
        tags = nltk.pos_tag(tokens)
        nouns = [token for token, pos in tags if pos.startswith('N')]
        verbs = [token for token, pos in tags if pos.startswith('V')]
        adverbs = [token for token, pos in tags if pos.startswith('W') or pos.startswith('RB')]
        numbers = [token for token, pos in tags if pos == "CD"]
        adjectives = [token for token, pos in tags if pos.startswith('J')]
        
        self.categories_dict = {
            "noun" : nouns,
            "verb" : verbs,
            "adverb" : adverbs,
            "number" : numbers,
            "adjective": adjectives
        }
        
        # For each token
        for token in tokens:
            # Check if token is a brand name
            if token in self.phones_df["brand"].str.lower().values:
                # Add the brand to the decision dictionary
                if "brand" not in self.decision_dict.keys():
                    self.decision_dict["brand"] = []
                
                self.decision_dict["brand"].append(self.searchNot(token))
            # Check if token is an os name
            elif token in self.phones_df["operating_system"].str.lower().values:
                # Add the os to the decision dictionary
                self.decision_dict["operating_system"] = self.searchNot(token)
            # Check if token is a unit name and does not have any column name nearby
            elif token in conv.Units:
                self.searchForAloneUnits(token)
            elif token in conv.Generations:
                self.decision_dict["generation"] = self.searchNot(token)
            else:
                # Check if column name or substring is a numeric column
                for column in reader.ColumnsNumeric:
                    if token in column and token not in conv.Units:
                        self.searchForQuantity(token, column)
                        break
                    
        # After analizing all tokens check if an answer can be done
        self.ui.saveContext(self.decision_dict)
        self.tryToAnswer()
        
    
    def loadContext(self, context):
        self.decision_dict = context
        print(context)
                        


            
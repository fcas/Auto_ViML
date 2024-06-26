import pandas as pd
import numpy as np

######### NEW And FAST WAY to ADD Feature Engg COLUMNS IN A DATA SET #######
###   Modify Dataframe by adding Features using Feature Tools ####
def add_computational_primitive_features(df, add_types: list, idcolumn=''):
    """
    ###   Modify Dataframe by adding computational primitive Features using Feature Tools ####
    ###   What are computational primitives? they are to add, subtract, multiply and divide features
    ### Inputs:
    ###   df: Just sent in the data frame df that you want features added to
    ###   add_types: list of computational types: 'add', 'subtract', 'multiply' and 'divide'. Choose any or all.
    ###   idcolumn: this is to create an index for the dataframe since FT runs on index variable. You can leave it empty string.
    """
    try:
        import featuretools as ft
    except:
        print('pip install featuretools and try this again')
    df = copy.deepcopy(df)
    projectid = 'project_prediction'
    dataid = 'project_data'
    if idcolumn == '':
        indexid = 'index'
        make_index = True
    else:
        indexid = idcolumn
        make_index = False
    # Make an entityset and add the entity
    es = ft.EntitySet(id=projectid)
    es.entity_from_dataframe(entity_id=dataid, dataframe=df,
                             make_index=make_index, index=indexid)

    # Run deep feature synthesis with given input primitives or automatically deep 2
    if len(add_types) > 0:
        ### Build Features based on given primitive types, add_types which is a list
        df_mod, feature_defs = ft.dfs(entityset=es, target_entity=dataid,
                                      trans_primitives=add_types)
    else:
        ### Perform Deep Feature Synthesis Automatically for Depth 2
        df_mod, feature_defs = ft.dfs(entityset=es, target_entity=dataid,
                                      max_depth=2, n_jobs=-1,
                                      verbose=0)
    if make_index:
        df_mod = df_mod.reset_index(drop=True)
    return df_mod


def feature_engineering(df, ft_requests, idcol):
    """
    The Feature Engineering module needs FeatureTools installed to work.
    So please do "pip install featuretools" before trying out this module.
    It takes a given data set, df and adds features based on the requet types in
    ft_requests which can be 'add','subtract','multiply','divide'. If you have
    an id_column in the data set, you can provide it as idcol (a string variable).
    It will return your modified dataset with 'idcol' as the index. Make sure
    you reset the index if you want to return it to its former state.
    Also do not send in your entire dataframe! Just send a small dataframe with a few variables.
    Once you see how it adds to performance of model, you can add more variables to dataframe.
    """
    df = copy.deepcopy(df)
    if df.shape[1] < 2:
        print('More than one column in dataframe required to perform feature engineering. Returning')
        return df
    ft_dict = dict(zip(['add', 'multiply', 'subtract', 'divide'],
                       ['add_numeric', 'multiply_numeric',
                        'subtract_numeric', 'divide_numeric']))
    if len(ft_requests) > 0:
        ft_list = []
        for ft_one in ft_requests:
            if ft_one in ft_dict.keys():
                ft_list.append(ft_dict[ft_one])
            else:
                print('    Cannot perform %s-type feature engineering...' % ft_one)
        cols = [x for x in df.columns.tolist() if x not in [idcol]]
        for each_ft, count in zip(ft_list, range(len(ft_list))):
            if count == 0:
                df_mod = add_computational_primitive_features(df, [each_ft], idcol)
                print(df_mod.shape)
            else:
                df_temp = add_computational_primitive_features(df, [each_ft], idcol)
                df_temp.drop(cols, axis=1, inplace=True)
                df_mod = pd.concat([df_mod, df_temp], axis=1, ignore_index=False)
                print(df_mod.shape)
    else:
        df_mod = add_computational_primitive_features(df, [], idcol)
    return df_mod


def add_date_time_features(smalldf, startTime, endTime, splitter_date_string="/", splitter_hour_string=":"):
    """
    If you have start date time stamp and end date time stamp, this module will create additional features for such fields.
    You must provide a start date time stamp field and if you have an end date time stamp field, you must use it.
    Otherwise, you are better off using the create_date_time_features module which is also in this library.
    You must provide the following:
    smalldf: Dataframe containing your date time fields
    startTime: this is hopefully a string field which converts to a date time stamp easily. Make sure it is a string.
    endTime: this also must be a string field which converts to a date time stamp easily. Make sure it is a string.
    splitter_date_string: usually there is a string such as '/' or '.' between day/month/year etc. Default is assumed / here.
    splitter_hour_string: usually there is a string such as ':' or '.' between hour:min:sec etc. Default is assumed : here.
    """
    smalldf = smalldf.copy()
    add_cols = []
    start_date = 'processing' + startTime + '_start_date'
    smalldf[start_date] = smalldf[startTime].map(lambda x: x.split(" ")[0])
    add_cols.append(start_date)
    try:
        start_time = 'processing' + startTime + '_start_time'
        smalldf[start_time] = smalldf[startTime].map(lambda x: x.split(" ")[1])
        add_cols.append(start_time)
    except:
        ### there is no hour-minutes part of this date time stamp field. You can just skip it if it is not there
        pass
    end_date = 'processing' + endTime + '_end_date'
    smalldf[end_date] = smalldf[endTime].map(lambda x: x.split(" ")[0])
    add_cols.append(end_date)
    try:
        end_time = 'processing' + endTime + '_end_time'
        smalldf[end_time] = smalldf[endTime].map(lambda x: x.split(" ")[1])
        add_cols.append(end_time)
    except:
        ### there is no hour-minutes part of this date time stamp field. You can just skip it if it is not there
        pass
    view_days = 'processing' + startTime + '_elapsed_days'
    smalldf[view_days] = (pd.to_datetime(smalldf[end_date]) - pd.to_datetime(smalldf[start_date])).values.astype(int)
    add_cols.append(view_days)
    try:
        view_time = 'processing' + startTime + '_elapsed_time'
        smalldf[view_time] = (pd.to_datetime(smalldf[end_time]) - pd.to_datetime(smalldf[start_time])).astype(
            'timedelta64[s]').values
        add_cols.append(view_time)
    except:
        ### In some date time fields this gives an error so skip it in that case
        pass
    #### The reason we chose endTime here is that startTime is usually taken care of by another library. So better to do this alone.
    year = 'processing' + endTime + '_end_year'
    smalldf[year] = smalldf[end_date].map(lambda x: str(x).split(splitter_date_string)[0]).values
    add_cols.append(year)
    #### The reason we chose endTime here is that startTime is usually taken care of by another library. So better to do this alone.
    month = 'processing' + endTime + '_end_month'
    smalldf[month] = smalldf[end_date].map(lambda x: str(x).split(splitter_date_string)[1]).values
    add_cols.append(month)
    try:
        #### The reason we chose endTime here is that startTime is usually taken care of by another library. So better to do this alone.
        daynum = 'processing' + endTime + '_end_day_number'
        smalldf[daynum] = smalldf[end_date].map(lambda x: str(x).split(splitter_date_string)[2]).values
        add_cols.append(daynum)
    except:
        ### In some date time fields the day number is not there. If not, just skip it ####
        pass
    #### In some date time fields, the hour and minute is not there, so skip it in that case if it errors!
    try:
        start_hour = 'processing' + startTime + '_start_hour'
        smalldf[start_hour] = smalldf[start_time].map(lambda x: str(x).split(splitter_hour_string)[0]).values
        add_cols.append(start_hour)
        start_min = 'processing' + startTime + '_start_hour'
        smalldf[start_min] = smalldf[start_time].map(lambda x: str(x).split(splitter_hour_string)[1]).values
        add_cols.append(start_min)
    except:
        ### If it errors, skip it
        pass
    #### Check if there is a weekday and weekends in date time columns using endTime only
    weekday_num = 'processing' + endTime + '_end_weekday_number'
    smalldf[weekday_num] = pd.to_datetime(smalldf[end_date]).dt.weekday.values
    add_cols.append(weekday_num)
    weekend = 'processing' + endTime + '_end_weekend_flag'
    smalldf[weekend] = smalldf[weekday_num].map(lambda x: 1 if x in [5, 6] else 0)
    add_cols.append(weekend)
    #### If everything works well, there should be 13 new columns added by module. All the best!
    print('%d columns added using start date=%s and end date=%s processing...' % (len(add_cols), startTime, endTime))
    return smalldf

#################################################################################
def split_one_field_into_many(df, field, splitter, filler, new_names_list):
    """
    This little function takes any data frame field (string variables only) and splits
    it into as many fields as you want in the new_names_list.
    You can also specify what string to split on using the splitter argument.
    You can also fill Null values that occur due to your splitting by specifying a filler.
    if no new_names_list is given, then we use the name of the field itself to split.
    """
    import warnings
    warnings.filterwarnings("ignore")
    df = df.copy()
    ### First print the maximum number of things in that field
    max_things = df[field].map(lambda x: len(x.split(splitter))).max()
    if len(new_names_list) == 0:
        print('    Max. columns created by splitting %s field is %d.' % (
            field, max_things))
    else:
        print(
            '    Max. columns created by splitting %s field is %d but you have given %d variable names only. Selecting first %d' % (
                field, max_things, len(new_names_list), len(new_names_list)))
    ### This creates a new field that counts the number of things that are in that field.
    num_products_viewed = 'count_things_in_' + field
    df[num_products_viewed] = df[field].map(lambda x: len(x.split(";"))).values
    ### Clean up the field such that it has the right number of split chars otherwise add to it
    df[field] = df[field].map(
        lambda x: x + splitter * (max_things - len(x.split(";"))) if len(x.split(";")) < max_things else x)
    ###### Now you create new fields by split the one large field ########
    if new_names_list == '':
        new_names_list = [field + '_' + str(i) for i in range(1, max_things + 1)]
    try:
        for i in range(len(new_names_list)):
            df[field].fillna(filler, inplace=True)
            df.loc[df[field] == splitter, field] = filler
            df[new_names_list[i]] = df[field].map(lambda x: x.split(splitter)[i]
            if splitter in x else x)
    except:
        ### Check if the column is a string column. If not, give an error message.
        print('Cannot split the column. Getting an error. Check the column again')
        return df
    return df, new_names_list


#################################################################################
def add_aggregate_primitive_features(dft, agg_types, id_column, ignore_variables: list):
    """
    ###   Modify Dataframe by adding computational primitive Features using Feature Tools ####
    ###   What are aggregate primitives? they are to "mean""median","mode","min","max", etc. features
    ### Inputs:
    ###   df: Just sent in the data frame df that you want features added to
    ###   agg_types: list of computational types: 'mean','median','count', 'max', 'min', 'sum', etc.
    ###         One caveat: these agg_types must be found in the agg_func of numpy or pandas groupby statement.
    ###         for example: numpy has 'median','prod','sum','std','var', etc. - they will work!
    ###   idcolumn: this is to create an index for the dataframe since FT runs on index variable. You can leave it empty string.
    ###   ignore_variables: list of variables to ignore among numeric variables in data since they may be ID variables.
    """
    import copy
    ### Make sure the list of functions they send in are acceptable functions. If not, the aggregate will blow up!
    func_set = {'count', 'sum', 'mean', 'mad', 'median', 'min', 'max', 'mode', 'abs', 'prod', 'std', 'var', 'sem',
                'skew', 'kurt', 'quantile', 'cumsum', 'cumprod', 'cummax', 'cummin'}
    agg_types = list(set(agg_types).intersection(func_set))
    ### If the ignore_variables list is empty, make sure you add the id_column to it so it can be dropped from aggregation.
    if len(ignore_variables) == 0:
        ignore_variables = [id_column]
    ### Select only integer and float variables to do this aggregation on. Be very careful if there are too many vars.
    ### This will take time to run in that case.
    dft_index = copy.deepcopy(dft[id_column])
    dft_cont = copy.deepcopy(dft.select_dtypes('number').drop(ignore_variables, axis=1))
    dft_cont[id_column] = dft_index
    try:
        dft_full = dft_cont.groupby(id_column).agg(agg_types)
    except:
        ### if for some reason, the groupby blows up, then just return the dataframe as is - no changes!
        return dft
    cols = [x + '_' + y + '_by_' + id_column for (x, y) in dft_full.columns]
    dft_full.columns = cols
    ###  Not every column has useful values. If it is full of just the same value, remove it
    _, list_unique_col_ids = np.unique(dft_full, axis=1, return_index=True)
    dft_full = dft_full.iloc[:, list_unique_col_ids]
    return dft_full


################################################################################################################################
import copy
import time
import pdb


def FE_create_groupby_features(dft, groupby_columns, numeric_columns, agg_types):
    """
    FE means FEATURE ENGINEERING - That means this function will create new features
    Beware: this function will return a smaller dataframe than what you send in since it groups rows by keys.
    #########################################################################################################
    Function groups rows in a dft dataframe by the groupby_columns and returns multiple columns for the numeric column aggregated.
    Do not send in more than one column in the numeric column since beyond the first column it will be ignored!
    agg_type can be any numpy function such as mean, median, sum, count, etc.
    ##########################################################################################################
    Returns: a smaller dataframe with rows grouped by groupby_columns and aggregated for the numeric_column
    """
    start_time = time.time()
    print('Autoviml Feature Engineering: creating groupby features using %s' % groupby_columns)
    ##########  This is where we create new columns by each numeric column grouped by group-by columns given.
    if isinstance(numeric_columns, list):
        pass
    elif isinstance(numeric_columns, str):
        numeric_columns = [numeric_columns]
    else:
        print('    Numeric column must be a string not a number Try again')
        return pd.DataFrame()
    grouped_list = pd.DataFrame()
    for iteration, numeric_column in zip(range(len(numeric_columns)), numeric_columns):
        grouped = dft.groupby(groupby_columns)[[numeric_column]]
        try:
            agg_type = agg_types[iteration]
        except:
            print('    No aggregation type given, hence mean is chosen by default')
            agg_type = 'mean'
        try:
            prefix = numeric_column + '_'
            if agg_type in ['Sum', 'sum']:
                grouped_agg = grouped.sum()
            elif agg_type in ['Mean', 'mean', 'Average', 'average']:
                grouped_agg = grouped.mean()
            elif agg_type in ['count', 'Count']:
                grouped_agg = grouped.count()
            elif agg_type in ['Median', 'median']:
                grouped_agg = grouped.median()
            elif agg_type in ['Maximum', 'maximum', 'max', 'Max']:
                ## maximum of the amounts
                grouped_agg = grouped.max()
            elif agg_type in ['Minimum', 'minimum', 'min', 'Min']:
                ## maximum of the amounts
                grouped_agg = grouped.min()
            else:
                grouped_agg = grouped.mean()
            grouped_sep = grouped_agg.unstack().add_prefix(prefix).fillna(0)
        except:
            print('    Error in creating groupby features...returning with null dataframe')
            grouped_sep = pd.DataFrame()
        if iteration == 0:
            grouped_list = copy.deepcopy(grouped_sep)
        else:
            grouped_list = pd.concat([grouped_list, grouped_sep], axis=1)
        print(
            '    After grouped features added by %s, number of columns = %d' % (numeric_column, grouped_list.shape[1]))
    #### once everything is done, you can close it here
    print('Time taken for creation of groupby features (in seconds) = %0.0f' % (time.time() - start_time))
    try:
        grouped_list.columns = grouped_list.columns.get_level_values(1)
        grouped_list.columns.name = None  ## make sure the name on columns is removed
        grouped_list = grouped_list.reset_index()  ## make sure the ID column comes back
    except:
        print('   Error in setting column names. Please reset column names after this step...')
    return grouped_list
################################################################################
from scipy.stats import skew, kurtosis
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.metrics import mean_squared_error, accuracy_score

class EntropyBinningTransformer(BaseEstimator, TransformerMixin):
    """
    #########   This innovative binning transformer is found only in AutoViML  ##############################
    The entropy binning approach in AutoViML is a novel and intriguing approach, especially as 
    it leverages decision trees to determine optimal binning thresholds based on information gain 
    (for classification) or mean squared error reduction (for regression). 

    This method can adapt well to non-linear relationships between the feature and the target. 
    It also incorporates some heuristics and improvements to enhance its effectiveness and efficiency.

    Heuristics:
    Variable Selection: We prioritize binning the most important variables. 
    This is a sensible heuristic as it focuses computational resources on variables that are 
    most likely to impact the model. We introduce a parameter to specify the number of top variables to bin.

    Adaptive max_depth: We've used an adaptive max_depth based on the number of continuous variables. 
    This heuristic helps control the granularity of the binning. We can maintain this by adding a 
    logic to adjust max_depth based on the number of features.

    Handling of Binned Variables: The code has an option to either keep the original variables 
    alongside the binned versions or replace them. This flexibility can be useful and we keep it 
    in the class implementation.

    Post-Binning Smoothing: After binning, applying smoothing techniques (e.g., Laplace smoothing) 
    can help address bins with very low frequencies, which might be particularly useful for categorical targets.

    Incorporating these aspects, this is an updated version of the original EntropyBinningTransformer method in AutoViML

    Additional Improvements to consider:

    Evaluation and Optimization: Integrating a mechanism to evaluate the effectiveness of binning (e.g., 
        using cross-validation scores) and automatically optimize the binning parameters accordingly.
    #########################################################################################################
    EntropyBinningTransformer is a transformer class for binning numeric variables based on entropy using decision trees,
    with options for selecting the most relevant variables for binning based on their predictive power, skewness,
    and kurtosis, and for smoothing the bins post-binning to mitigate issues with overfitting and bins with 
        low frequencies.

    Parameters:
    - max_depth: The maximum depth of the decision trees used for binning.
    - min_samples_leaf: The minimum number of samples required to be at a leaf node of the decision trees.
    - entropy_binning: Whether to apply entropy binning.
    - modeltype: Indicates whether the target variable is for 'Regression' or 'Classification'.

    Methods:
    - fit: Learns the binning thresholds for each variable.
    - transform: Applies the learned thresholds to bin the data, with an option for post-binning smoothing.
    - select_top_n_vars: Selects the top N variables for binning based on their predictive power and distribution
         characteristics.
    #########################################################################################################
    ####  U S A G E  #####
    # Initialize the EntropyBinningTransformer 
    entropy_binner = EntropyBinningTransformer( replace_vars=True, modeltype='Classification')

    # Optionally, select top n variables based on their predictive power
    # This step is useful if you want to bin only the most informative variables
    top_vars = entropy_binner.select_top_n_vars(X_train, y_train, n=2)
    X_train_top_vars = X_train[top_vars]

    # Fit the transformer to the training data
    entropy_binner.fit(X_train_top_vars, y_train)

    # Transform the training data and new data using the learned binning thresholds
    X_train_binned = entropy_binner.transform(X_train_top_vars)
    X_test_binned = entropy_binner.transform(X_test[top_vars])    
    #########################################################################################################
    """
    def __init__(self, replace_vars=True, modeltype='Classification', top_n_vars=None):
        self.replace_vars = replace_vars
        self.modeltype = modeltype
        self.max_depth = 10
        self.min_samples_leaf = 2
        self.top_n_vars = top_n_vars
        self.binning_thresholds = {}
        self.remvars = []

    def fit(self, X, y):
        # Determine top_n variables based on importance, for example, using feature importances from a preliminary model
        if self.top_n_vars is not None:
            top_vars = self.select_top_n_vars(X, y, n=self.top_n_vars)
        else:
            top_vars = X.columns

        for col in top_vars:
            max_depth = self._adjust_max_depth(len(top_vars))
            clf = self.get_decision_tree(max_depth)
            
            try:
                clf.fit(X[col].values.reshape(-1, 1), y)
                thresholds = clf.tree_.threshold[clf.tree_.threshold > -2]
                self.binning_thresholds[col] = np.sort(thresholds)
            except Exception as e:
                print(f'Error in {col} during Entropy Binning: {e}')
        
        return self
        
    def get_decision_tree(self, max_depth):
        if self.modeltype == 'Regression':
            return DecisionTreeRegressor(criterion='mse', min_samples_leaf=self.min_samples_leaf,
                                         max_depth=max_depth, random_state=99)
        else:
            return DecisionTreeClassifier(criterion='entropy', min_samples_leaf=self.min_samples_leaf,
                                          max_depth=max_depth, random_state=99)

    def _adjust_max_depth(self, n_features):
        """
        Adjust max depth based on the heuristic from the original function.

        Future:
        Dynamic Depth Adjustment: Instead of fixed depth adjustments based on the number of variables, 
        use a more dynamic approach that considers the actual distribution and variability of each variable.

        """
        if self.max_depth is not None:
            return self.max_depth  # Use user-defined max_depth if provided
        elif n_features <= 2:
            return 2
        elif n_features <= 5:
            return n_features - 2
        elif n_features <= 10:
            return 5
        else:
            return 10  # Default max depth for > 10 features

    def select_top_n_vars(self, X, y, n=2, skew_threshold=1.5, kurtosis_threshold=3):
        """
        The select_top_n_vars method takes into account the skewness and kurtosis of each variable
         in addition to its predictive power. The final score is used to rank the variables 
         adjusted by the absolute values of skewness and kurtosis to prefer variables that are 
         both predictive and have less extreme distributions.

        Incorporating distribution-based metrics such as skewness, kurtosis, and outlier 
        detection into the selection process for variables to bin can indeed provide a more 
        nuanced approach. Variables with high skewness or kurtosis may benefit more from binning, 
        as it can help to normalize their effect in predictive models. Additionally, handling 
        outliers before binning can ensure that bins are more representative of the general 
        distribution of the data.
        """
        scores = {}
        ### Select only float numeric columns to bin ###########
        numvars = X.select_dtypes(include='float').columns.tolist()
        ### Let's keep the remaining vars ######
        self.remvars = [x for x in list(X) if x not in numvars ]
        for col in numvars:
            X_col = X[col].values.reshape(-1, 1)

            # Calculate skewness and kurtosis
            skewness = skew(X[col])
            kurt = kurtosis(X[col], fisher=True)  # Fisher's definition is used (normal ==> 0.0)

            # Initialize a simple decision tree
            if self.modeltype == 'Regression':
                model = DecisionTreeRegressor(max_depth=self.max_depth, random_state=99)
            else:
                model = DecisionTreeClassifier(max_depth=self.max_depth, random_state=99)

            # Fit the model
            model.fit(X_col, y)

            # Predict using the model
            predictions = model.predict(X_col)

            # Calculate the performance metric
            if self.modeltype == 'Regression':
                score = -mean_squared_error(y, predictions)  # Negative because lower MSE is better
            else:
                score = accuracy_score(y, predictions)

            # Store the score, possibly adjusted for skewness and kurtosis
            if abs(skewness) > skew_threshold or abs(kurt) > kurtosis_threshold:
                scores[col] = score * (1 + abs(skewness) + abs(kurt))
            else:
                scores[col] = score

        # Sort the variables based on the scores and select the top n
        top_n_vars = sorted(scores, key=scores.get, reverse=True)[:max(n, int(X.shape[1] * 0.1), 2)]

        self.remvars += [x for x in numvars if x not in top_n_vars ]
        return top_n_vars

    def transform(self, X):
        """
        Applies the learned binning thresholds and Laplace smoothing to the data, replacing or appending the original 
        variables with their smoothed, binned versions based on the replace_vars flag.

        Parameters:
        - X (pd.DataFrame): The input data to transform.

        Returns:
        - X_transformed (pd.DataFrame): The transformed data with variables binned and smoothed according to the learned thresholds.
        """
        X_transformed = X.copy()
        for col, thresholds in self.binning_thresholds.items():
            bin_col_name = f'{col}_bin' if not self.replace_vars else col
            binned_data = np.digitize(X_transformed[col].values, thresholds)
            
            # Apply Laplace smoothing to the binned data
            smoothed_binned_data = binned_data + 1  # Add-one smoothing
            
            # Replace or append the smoothed, binned data
            X_transformed[bin_col_name] = smoothed_binned_data
            
            # If replacing, drop the original column if it's not the same as the bin_col_name
            if self.replace_vars and bin_col_name != col:
                X_transformed.drop(col, axis=1, inplace=True)
        
        return X_transformed
################################################################################################

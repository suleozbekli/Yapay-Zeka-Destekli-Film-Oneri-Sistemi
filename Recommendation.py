from pyspark.sql import SparkSession 
from pyspark.sql.functions import  col, regexp_replace, when, lit ,trim,initcap
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import CrossValidator,ParamGridBuilder
import matplotlib.pyplot as plt


spark = SparkSession.builder.appName('recommender_system').getOrCreate()

file_location = r'C:\Users\user\Desktop\Büyük Veri\movie_ratings_df.csv'

# inferschema otomatik integer mi string mi anlamayı sağlıyor
df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(file_location)
#print(" \n\nDataset {:d} satır ve {:d} sütundan oluşmaktadır.".format(df.count() ,len(df.columns)))

#print("Dataframe Schema:")
#df.printSchema()

#print("Null değerleri içeren satırlar:")
df.filter((col('userId').isNull()) | (col('rating').isNull()) | (col('title').isNull()))#.show()
df = df.dropna(subset=['userId', 'rating', 'title'])

#print("Null değerler çıkartıldı. Yeni veri sayısı:",df.count()) # bu kod boş değerler çıkartılmış halini konsola yazdırır.


duplicate_count= df.count() - df.dropDuplicates(['userId', 'title', 'rating']).count()    # tekrar eden satırları bulur.
#print("\nTekrar eden satırların sayısı :" ,duplicate_count)                                    

duplicate_rows = df.groupBy('userId', 'title', 'rating').count().filter(col('count') > 1)
#print("Tekrar eden satırlardan örnek:")
#duplicate_rows.show(20)





df = df.dropDuplicates(['userId', 'title', 'rating'])
#print("Tekrar edenler çıkartıldı. Yeni veri sayısı: \n", df.count())
#print("cleaning işlemi başlıyor...")

def Clean_titles(df):
    #print("Tüm filmlerin ilk harfleri büyük yazılıyor..")
    title_initcap_df = df.withColumn("title", initcap(col("title")))
    #title_initcap_df.show(5)

    #print("Noktalama kaldırılıyor...")
    trimmed_new_df = title_initcap_df.withColumn("title", trim(col("title")))
    #trimmed_new_df.show(5)

    #print("Gereksiz karakterler ve noktalama siliniyor...")
    regex_new_df = trimmed_new_df.withColumn("title", regexp_replace(col("title"), "[^a-zA-Z0-9\\s]", ""))
    #regex_new_df.show(5)

    #print("Rating değeri 5'ten büyük olanları 5'e eşitleme...")
    cleaned_df = regex_new_df.withColumn("rating", when(col("rating") > 5, 5).otherwise(col("rating")))
    #cleaned_df.show(5)
 
    return cleaned_df

df = Clean_titles(df)   

#ratings = df.select("rating")
#rating_counts = ratings.groupBy("rating").count().orderBy("rating")
#rating_counts_pandas = rating_counts.toPandas()
#colors = ['red', 'green', 'blue', 'orange', 'purple']
#plt.bar(rating_counts_pandas["rating"], rating_counts_pandas["count"], color=colors)
#plt.xlabel("Rating")
#plt.ylabel("Count")
#plt.title("Rating Distribution")       
#plt.show()
#for index, row in rating_counts_pandas.iterrows():
   # print(f"Rating {row['rating']}: {row['count']} adet")     # hangi puanların kaç kere verildiğini gösterir.




stringIndexer = StringIndexer(inputCol='title', outputCol='title_new')
model = stringIndexer.fit(df)
indexed = model.transform(df)
#print("title_new sonuçları:")
#indexed.show(5)  # burda ml hazırlığı için bütün film isimleri birer sayısal değere dönüştürüldü.


train, test = indexed.randomSplit([0.8,0.2])
#print("Training set size:",train.count())
#print("Test set size:",test.count())

def cross_validation(train):
    k = 5
    alsalg = ALS(maxIter=10,
                 regParam=0.01,
                 userCol='userId',
                 itemCol='title_new',
                 ratingCol='rating',
                 nonnegative=True,
                 coldStartStrategy="drop")

    paramgrid = ParamGridBuilder().addGrid(alsalg.rank, [12, 27]).addGrid(alsalg.regParam, [0.01, 0.1]).addGrid(alsalg.maxIter, [8]).build()
    crossvalidation = CrossValidator(estimator=alsalg,
                                     estimatorParamMaps=paramgrid,
                                     evaluator=RegressionEvaluator(metricName="rmse", predictionCol="prediction", labelCol="rating"), # değerlendirme için kullanılacak hata fonksiyonu
                                     numFolds=k,
                                     collectSubModels=True)
    crossvalmodel = crossvalidation.fit(train) # modelin oluşturulması 
    return crossvalmodel

#print("5 katlı çapraz doğrulama yapılıyor...")
cv_model = cross_validation(train) # modelin eğitilmesi


#def SumarizedModels(cv_model):
    #for k, models in enumerate(cv_model):
        #print("----------------{:d}-------------\n".format(k+1))
        #for i , n in enumerate(models):
            #print(i+1)
            #print("Model özeti{}".format(n))
        #print("-------------------------------------\n")    
#SumarizedModels(cv_model.subModels)

#for i, rmse in enumerate(cv_model.avgMetrics):
    #print("Rmse {:d} : {:.3f}".format(i+1,rmse))

#print("En iyi model: {} ".format(cv_model.bestModel))

predicted_ratings=cv_model.transform(test) # tahminlerin hesaplanması 
#print("tahminler hesaplandı. Bazı sonuçlar:")
#predicted_ratings.show(5)
selected_columns = ["userId", "title_new", "rating", "prediction"]
top_5_high_predictions = predicted_ratings.orderBy(col("prediction").desc()).select(selected_columns) #.show(5)
evaluator=RegressionEvaluator(metricName='rmse',predictionCol='prediction',labelCol='rating')
rmse=evaluator.evaluate(predicted_ratings)
#print("RMSE:",rmse)

#cv_model.bestModel.recommendForAllUsers(10).show(10)
    
def top_movies(user_id,n):
    unique_movies=indexed.select('title_new').distinct()
    a = unique_movies.alias('a')
    watched_movies=indexed.filter(indexed['userId'] == user_id).select('title_new')

    b=watched_movies.alias('b')
    total_movies = a.join(b, a.title_new == b.title_new,how='left')

    remaining_movies=total_movies.where(col("b.title_new").isNull()).select(a.title_new).distinct()
    remaining_movies=remaining_movies.withColumn("userId",lit(int(user_id)))
    recommendations=cv_model.transform(remaining_movies).orderBy('prediction',ascending=False).limit(n)
    
    
    movie_title = IndexToString(inputCol="title_new", outputCol="title",labels=model.labels)
    final_recommendations=movie_title.transform(recommendations)
    
    return final_recommendations#.show(n,False)

#print("Seçilen kişi için film önerileri:")
#top_movies(551,4)

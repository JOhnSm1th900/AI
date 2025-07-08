from flask import Blueprint, jsonify
from flask_restful import Api, Resource, reqparse
from flask_login import login_required, current_user
import numpy as np, pandas as pd, joblib, tensorflow as tf
from models import db, Prediction

bp = Blueprint('api', __name__)
api = Api(bp)


dl = tf.keras.models.load_model('models/dl_model.h5')
rf = joblib.load('models/rf_model.joblib')
scaler = joblib.load('models/scaler.joblib') 
extractor = tf.keras.Model(inputs=dl.input, outputs=dl.layers[-2].output)

parser = reqparse.RequestParser()
for feat in ['age','sex','cp','trestbps','chol','fbs','restecg','thalch','exang','oldpeak','slope','ca','thal']:
    parser.add_argument(feat, type=float, required=True)

numerical_features_to_scale = ['age', 'trestbps', 'chol', 'thalch', 'oldpeak']

# تعريف الميزات الفئوية وقيمها الأصلية (كما كانت في بيانات التدريب قبل الترميز الأحادي)
# يجب عليك التأكد من أن هذه التعيينات صحيحة بناءً على بيانات التدريب الأصلية وكيف تم التعامل معها.
categorical_features_mapping = {
    'sex': {0: 'Female', 1: 'Male'},
    'cp': {0: 'asymptomatic', 1: 'atypical angina', 2: 'non-anginal', 3: 'typical angina'},
    'fbs': {0: False, 1: True},
    'restecg': {0: 'lv hypertrophy', 1: 'normal', 2: 'st-t abnormality'},
    'exang': {0: False, 1: True},
    'slope': {0: 'downsloping', 1: 'flat', 2: 'upsloping'},
    'ca': {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}, 
    'thal': {0: 'fixed defect', 1: 'normal', 2: 'reversable defect', 3: 'reversable defect'} 
}
categorical_feature_names = list(categorical_features_mapping.keys())


# تعريف الأعمدة النهائية المتوقعة بعد الترميز الأحادي للميزات الفئوية فقط
expected_scaled_categorical_columns = [
    'sex_Male',
    'cp_atypical angina', 'cp_non-anginal', 'cp_typical angina',
    'fbs_True',
    'restecg_normal', 'restecg_st-t abnormality',
    'exang_True',
    'slope_flat', 'slope_upsloping',
    'ca_1.0', 'ca_2.0', 'ca_3.0',
    'thal_normal', 'thal_reversable defect'
]


class Predict(Resource):
    @login_required
    def post(self):
        args = parser.parse_args()
        print(args)
        
        # فصل الميزات العددية عن الفئوية
        numerical_input_data = {feat: [args[feat]] for feat in numerical_features_to_scale}
        categorical_input_data = {feat: [args[feat]] for feat in categorical_feature_names}

        df_numerical = pd.DataFrame(numerical_input_data)
        df_categorical = pd.DataFrame(categorical_input_data)
        
        # تحويل المدخلات الفئوية العددية إلى قيمها الأصلية (سلاسل نصية/منطقية)
        df_for_dummies = df_categorical.copy()
        for col, mapping in categorical_features_mapping.items():
            if col in df_for_dummies.columns:
                df_for_dummies[col] = df_for_dummies[col].map(mapping)
                
        # إجراء الترميز الأحادي (One-Hot Encoding) على الميزات الفئوية
        df_onehot = pd.get_dummies(df_for_dummies, columns=categorical_feature_names, drop_first=True)
        
        # التأكد من وجود جميع الأعمدة المرمزة أحاديا المتوقعة (15 عمود)
        # وملء القيم المفقودة بـ 0 إذا لم تظهر فئة معينة في الإدخال
        df_onehot_aligned = pd.DataFrame(0, index=[0], columns=expected_scaled_categorical_columns)
        for col in df_onehot_aligned.columns:
            if col in df_onehot.columns:
                df_onehot_aligned[col] = df_onehot[col].iloc[0]
                
        # تطبيق ال scaler على الميزات الفئوية المُرمزة أحاديًا (ال 15 ميزة)
        # هذا هو المكان الذي نُصلح فيه الخطأ بجعل المدخل 15 ميزة كما يتوقع ال scaler
        Xs = scaler.transform(df_onehot_aligned)

        # الحصول على Xdl (مخرجات مستخلص النموذج العميق)
        Xdl = extractor.predict(Xs)
        

        Xs_categorical_scaled = scaler.transform(df_onehot_aligned) # هذا هو Xs في الكود الأصلي
        
        # Xs ستكون ال 15 ميزة الفئوية المُوسعة والمُوسّعة (scaled)

        Xs = scaler.transform(df_onehot_aligned)
        
        #الحصول على Xdl (مخرجات مستخلص النموذج العميق)
        Xdl = extractor.predict(Xs)
        
        # دمج كل الميزات لنموذج Random Forest
        # هنا يتم دمج Xs (الميزات الفئوية ال 15 الموسعة) مع Xdl
        # الـ 5 ميزات الرقمية غير موجودة هنا في X.
        X = np.hstack([Xs, Xdl])
        
        y = int(rf.predict(X)[0]); probs = rf.predict_proba(X)[0].tolist()
        rec = (["مراجعة طبيب قلب","رسم قلب","متابعة مستمرة"]
                if y>=2 else ["نظام غذائي","رياضة","متابعة سنوية"])
        pr = Prediction(result=y, proba=probs, user=current_user._get_current_object())
        db.session.add(pr); db.session.commit()
        print(y,probs,rec)
        return jsonify(prediction=y, probabilities=probs, recommendations=rec)

class Health(Resource):
    def get(self): return {'status':'healthy'}, 200

class Dashboard(Resource):
    @login_required
    def get(self):
        data = [{'timestamp': p.timestamp.isoformat(),
                    'result': p.result,
                    'probabilities': p.proba}
                    for p in Prediction.query.filter_by(user_id=current_user.id)]
        return jsonify(predictions=data)



api.add_resource(Predict, '/predict')
api.add_resource(Health, '/health')
api.add_resource(Dashboard, '/dashboard')

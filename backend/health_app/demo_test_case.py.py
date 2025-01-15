import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from company.models import Financial_Data, company_list, Category, Group,SubCategory,company_valuation,category_multiply
from person.models import person_share
import pandas as pd
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from io import BytesIO
from django.db import connection
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def reset_sequences():
    """
    Automatically resets sequences for all tables in the database after each test.
    Ensures IDs restart from 1 if desired.
    """
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("""
            DO $$
            DECLARE
                seq RECORD;
            BEGIN
                FOR seq IN
                    SELECT c.oid::regclass::text AS sequence_name
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relkind = 'S'
                LOOP
                    EXECUTE format('ALTER SEQUENCE %I RESTART WITH 1', seq.sequence_name);
                END LOOP;
            END $$;
            """)


@pytest.fixture
def category_file():
    file_path = os.path.join(settings.MEDIA_ROOT, 'Category_data.xlsx')
    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(name='test_data.xlsx', content=f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@pytest.fixture
def group_file():
    file_path = os.path.join(settings.MEDIA_ROOT, 'group_data.xlsx')
    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(name='test_data.xlsx', content=f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@pytest.fixture
def subcategory_file():
    file_path = os.path.join(settings.MEDIA_ROOT, 'Subcategory_data.xlsx')
    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(name='test_data.xlsx', content=f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@pytest.fixture
def excel_file():
    file_path = os.path.join(settings.MEDIA_ROOT, 'financial_data.xlsx')
    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(name='test_data.xlsx', content=f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
@pytest.fixture
def category_subcategory_data():
    category = Category.objects.create(name='ENERGJI')
    subcategory = SubCategory.objects.create(name='NAFTË, GAZ DHE LËNDË DJEGËSE', category=category)
    category_1=Category.objects.create(name='PAJISJET DHE SHËRBIMET E ENERGJISË')
    subcategory_1 = SubCategory.objects.create(name='PAJISJET DHE SHËRBIMET E ENERGJISË', category=category_1)
    group=Group.objects.create(name='KASTRATI GROUP',reference_group_id='G4',founded_on='1999-01-12')
    return category, subcategory, category_1, subcategory_1, group

@pytest.fixture
def subcategory_company_data(api_client,subcategory_file,group_file):
    api_client.post(reverse('group_data_update'),{'file': group_file}, format='multipart')
    api_client.post(reverse('subcategory_data_update'), {'file': subcategory_file}, format='multipart')

@pytest.fixture
def financial_data(api_client, excel_file, subcategory_company_data):
    api_client.post(reverse('financial_data_update'), {'file': excel_file})
    
@pytest.fixture
def calculation_data( category_subcategory_data,financial_data):
    financial_data=Financial_Data.objects.all()
    multiple_first=category_multiply.objects.create(price_to_earnings=10,price_to_revenue=20,price_to_equity=30,subcategory=category_subcategory_data[1])
    multiple_second=category_multiply.objects.create(price_to_earnings=10,price_to_revenue=20,price_to_equity=30,subcategory=category_subcategory_data[3])
    company_valuation.objects.create(day=1,month=1,year=2018,valuation=((financial_data[9].capital*multiple_first.price_to_equity)+(financial_data[9].total_income*multiple_first.price_to_revenue)+(financial_data[9].profit_loss_before_tax*multiple_first.price_to_earnings))/3,company=financial_data[9],multiple=multiple_first)
    company_valuation.objects.create(day=1,month=1,year=2017,valuation=((financial_data[0].capital*multiple_first.price_to_equity)+(financial_data[0].total_income*multiple_first.price_to_revenue)+(financial_data[0].profit_loss_before_tax*multiple_first.price_to_earnings))/3,company=financial_data[0],multiple=multiple_first)
    company_valuation.objects.create(day=1,month=1,year=2018,valuation=((financial_data[10].capital*multiple_second.price_to_equity)+(financial_data[10].total_income*multiple_second.price_to_revenue)+(financial_data[10].profit_loss_before_tax*multiple_second.price_to_earnings))/3,company=financial_data[10],multiple=multiple_second)
    company_valuation.objects.create(day=1,month=1,year=2017,valuation=((financial_data[1].capital*multiple_second.price_to_equity)+(financial_data[1].total_income*multiple_second.price_to_revenue)+(financial_data[1].profit_loss_before_tax*multiple_second.price_to_earnings))/3,company=financial_data[1],multiple=multiple_second)


@pytest.fixture
def person_list_file():
    file_path = os.path.join(settings.MEDIA_ROOT, 'person_data.xlsx')
    with open(file_path, 'rb') as f:
        return SimpleUploadedFile(name='test_person_data.xlsx', content=f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
@pytest.fixture
def person_list_data(api_client,person_list_file):
    response = api_client.post(reverse('person_data_update'), {'file': person_list_file}, format='multipart')
@pytest.fixture
def person_share_data(api_client,financial_data):
    file_path = os.path.join(settings.MEDIA_ROOT, 'Ownership_data.xlsx')
    file=BytesIO(open(file_path, 'rb').read())
    response = api_client.post(reverse('ownership_data_update'), {'file': file,'year':2018}, format='multipart')

@pytest.fixture
def person_share_2017(api_client,financial_data):
    file_path = os.path.join(settings.MEDIA_ROOT, 'Ownership_data.xlsx')
    file=BytesIO(open(file_path, 'rb').read())
    response = api_client.post(reverse('ownership_data_update'), {'file': file,'year':2017}, format='multipart')

@pytest.mark.django_db
def test_category_file_generate_succesfully(api_client):
    url = reverse('category_data_generate')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=Category_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Category Data')
    assert df.shape[1] ==1
    assert len(df)==0

@pytest.mark.django_db
def test_category_file_update_succesfully(api_client, category_file):
    url = reverse('category_data_update')
    response = api_client.post(url, {'file': category_file}, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Category data updated successfully'
    assert Category.objects.count() == 4


@pytest.mark.django_db
def test_subcategory_file_generate_succesfully(api_client,financial_data):
    url = reverse('subcategory_data_generate')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=Subcategory_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Subcategory Data')
    assert df.shape[1] ==4
    assert len(df)==6

@pytest.mark.django_db
def test_subcategory_file_update_succesfully(api_client, subcategory_file):
    url = reverse('subcategory_data_update')
    response = api_client.post(url, {'file': subcategory_file}, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'SubCategory data updated successfully'
    assert Category.objects.count() == 4
    assert SubCategory.objects.count() == 6

@pytest.mark.django_db
def test_category_list_generate_succesfully(api_client, category_file, subcategory_file):
    api_client.post(reverse('category_data_update'), {'file': category_file}, format='multipart')
    api_client.post(reverse('subcategory_data_update'), {'file': subcategory_file}, format='multipart')
    response=api_client.get(reverse('category_list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4
    assert len(response.data[0]['sub category']) ==2

@pytest.mark.django_db
def test_category_list_generate_succesfully_if_there_is_no_data(api_client):
    response=api_client.get(reverse('category_list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0

@pytest.mark.django_db()
def test_generate_financial_data_by_year_excel_success(api_client):
    url = reverse('financial_data_generate',kwargs={'year': 2018})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')

@pytest.mark.django_db
def test_generate_financial_data_by_year_excel_no_data(api_client):
    url = reverse('financial_data_generate',kwargs={'year': 2018})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Financial Data')
    assert len(df) == 0

@pytest.mark.django_db
def test_generate_financial_data_by_year_excel_contain_all_coloumns(api_client):
    url = reverse('financial_data_generate',kwargs={'year': 2018})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Financial Data')
    assert df.shape[1] ==94

@pytest.mark.django_db
def test_generate_financial_data_by_year_excel_with_data(api_client,financial_data):
    url = reverse('financial_data_generate',kwargs={'year': 2018})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Financial Data')
    assert len(df) == 10

@pytest.mark.django_db()
def test_generate_financial_data_by_id_excel_success(api_client):
    url = reverse('financial_data_company_generate',kwargs={'nipt': 'K21711502v'})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')

@pytest.mark.django_db
def test_generate_financial_data_by_id_excel_no_data(api_client):
    url = reverse('financial_data_company_generate',kwargs={'nipt': 'K21711502v'})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Financial Data')
    assert len(df) == 0

@pytest.mark.django_db
def test_generate_financial_data_by_id_excel_contain_all_coloumns(api_client):
    url = reverse('financial_data_company_generate',kwargs={'nipt': 'K21711502v'})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Financial Data')
    assert df.shape[1] ==94

@pytest.mark.django_db
def test_generate_financial_data_by_id_excel_with_data(api_client,financial_data):
    url = reverse('financial_data_company_generate',kwargs={'nipt': 'K21711502v'})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=financial_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Financial Data')
    assert len(df) == 6
@pytest.mark.django_db
def test_successful_financial_data_update_if_data_is_valid(api_client, excel_file, subcategory_company_data):
    url = reverse('financial_data_update')
    response = api_client.post(url, {'file': excel_file}, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Financial data updated successfully'
    assert Financial_Data.objects.count() == 59
    assert Category.objects.count() == 4
    assert SubCategory.objects.count() == 6
    assert Group.objects.count() == 3
    assert company_list.objects.count() == 10

@pytest.mark.django_db
def test_successful_financial_data_create_if_new_data_is_valid_and_update_old_data(api_client, excel_file, subcategory_company_data):
    url = reverse('financial_data_update')
    response = api_client.post(url, {'file': excel_file}, format='multipart')
    df = pd.read_excel(excel_file)
    new_row = df.iloc[-1].copy()
    new_row['Viti Raportit'] = 2023
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, sheet_name='Financial Data')
    excel_buffer.seek(0)
    response = api_client.post(url, {'file': excel_buffer}, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Financial data updated successfully'
    assert Financial_Data.objects.count() == 60
    assert Category.objects.count() == 4
    assert SubCategory.objects.count() == 6
    assert Group.objects.count() == 3
    assert company_list.objects.count() == 10


@pytest.mark.django_db
def test_unsuccessful_of_financial_data_update_if_data_is_unvalid(api_client, excel_file):
    df = pd.read_excel(excel_file)
    row_index = df.index[-1] 
    df['Mjete monetare'] = df['Mjete monetare'].astype(object)
    df.at[row_index, 'Mjete monetare'] = 'data'
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, sheet_name='Financial Data')
    excel_buffer.seek(0)
    url = reverse('financial_data_update')
    response = api_client.post(url, {'file': excel_buffer}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_invalid_financial_data_file_type_give_error(api_client):
    invalid_content = b'%PDF-1.5\n\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n\n3 0 obj\n<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 595.276 841.89]/Contents 6 0 R/Annots 7 0 R>>\nendobj\n\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>\nendobj\n\n5 0 obj\n[ /PDF /Text ]\nendobj\n\n6 0 obj\n<</Length 44>>stream\nBT\n/F1 24 Tf\n100 100 Td\n(Hello, world!)Tj\nET\nendstream\nendobj\n\nxref\n0 7\n0000000000 65535 f\n0000000309 00000 n\n0000000015 00000 n\n0000000408 00000 n\n0000000218 00000 n\n0000000470 00000 n\n0000000525 00000 n\ntrailer\n<</Size 7/Root 1 0 R>>\nstartxref\n630\n%%EOF'
    invalid_file = BytesIO(invalid_content)
    url = reverse('financial_data_update')
    response = api_client.post(url, {'file': invalid_file}, format='multipart')
    assert response.status_code == 400
    assert 'Excel file format cannot be determined, you must specify an engine manually.' == response.data['error']


@pytest.mark.django_db
def test_financial_data_empty_file_will_not_change_data(api_client):
    url = reverse('financial_data_generate',kwargs={'year': 2000})
    response = api_client.get(url)
    empty_file = BytesIO(response.content)
    url = reverse('financial_data_update')
    response = api_client.post(url, {'file': empty_file}, format='multipart')
    assert response.status_code == 200
    assert Financial_Data.objects.filter(financial_year=2018).count() == 0
    

@pytest.mark.django_db
def test_unsuccessful_if_comapny_name_or_company_id_is_missing(api_client, excel_file):
    df = pd.read_excel(excel_file)
    row_index = df.index[-1] 
    df.at[row_index, 'NIPT'] = pd.NA
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, sheet_name='Financial Data')
    excel_buffer.seek(0)
    url = reverse('financial_data_update')
    response = api_client.post(url, {'file': excel_buffer}, format='multipart')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_profitwise_comapny_data_generate_correctly(api_client,financial_data,calculation_data):
    url = reverse('profitwise_company_data', kwargs={'year': 2018})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['profit'])==10
    assert response.data['profit'][0]['company'] == 'Banka Kombetare Tregtare'
    assert response.data['profit'][1]['company'] == 'Kastrati Group'
    assert response.data['profit'][2]['company'] == 'Gsa'
    assert response.data['profit'][0]['ranking_difference'] == 0
    assert response.data['profit'][1]['ranking_difference'] == 1
    assert response.data['profit'][2]['ranking_difference'] == 6
    assert len(response.data['revenue'])==10
    assert response.data['revenue'][0]['company'] == 'Kastrati Group'
    assert response.data['revenue'][1]['company'] == 'Kurum International Sh.A.'
    assert response.data['revenue'][2]['company'] == 'Banka Kombetare Tregtare'
    assert response.data['revenue'][0]['ranking_difference'] == 0
    assert response.data['revenue'][1]['ranking_difference'] == 6
    assert response.data['revenue'][2]['ranking_difference'] == -1
    assert len(response.data['valuation'])==2
    assert response.data['valuation'][0]['company'] == 'Kastrati Group'
    assert response.data['valuation'][1]['company'] == 'Furnizuesi I Shërbimit Universal'
    assert response.data['valuation'][0]['ranking_difference'] == 0
    assert response.data['valuation'][1]['ranking_difference'] == 0



@pytest.mark.django_db
def test_profitwise_comapny_data_generate_correctly_even_previous_year_data_not_available(api_client,financial_data,calculation_data):
    url = reverse('profitwise_company_data', kwargs={'year': 2017})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['profit'])==9
    assert len(response.data['revenue'])==9
    assert len(response.data['valuation'])==2

@pytest.mark.django_db
def test_profitwise_comapny_data_generate_correctly_even_one_of_company_previous_year_data_not_available(api_client,financial_data,calculation_data):
    Financial_Data.objects.first().delete()
    url = reverse('profitwise_company_data', kwargs={'year': 2018})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['profit'])==10
    assert len(response.data['revenue'])==10
    assert len(response.data['valuation'])==2
@pytest.mark.django_db
def test_profitwise_comapny_data_generate_correctly_even_id_data_is_not_available(api_client,financial_data):
    Financial_Data.objects.first().delete()
    url = reverse('profitwise_company_data', kwargs={'year': 2016})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['profit'])==0
    assert len(response.data['revenue'])==0
    assert len(response.data['valuation'])==0

@pytest.mark.django_db
def test_company_profile_not_give_error_when_company_id_not_exist(api_client):
    base_url = reverse('company_profile')
    url = f"{base_url}?name=abc&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_company_profile_generate_correct_data_when_company_id_exist(api_client,financial_data):
    base_url = reverse('company_profile')
    url = f"{base_url}?name=KASTRATI GROUP&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Kastrati Group'
    assert response.data['category'] == 'Energji'
    assert response.data['subcategory'] == 'Naftë, Gaz Dhe Lëndë Djegëse'
    assert response.data['profit_each_year'] == {'2017': 1200957059.0, '2018': 1470269638.0}
    assert response.data['owners']==[]

@pytest.mark.django_db
def test_category_multiple_data_created_succesfully_if_there_is_no_exist_record(api_client,financial_data):
    id=Financial_Data.objects.first().company.subcategory.subcategory_id
    url=reverse('add_multiple')
    response=api_client.post(url,{'price_to_earnings':1,'price_to_revenue':1,'price_to_equity':1.5,'subcategory_id':id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']=='Created successfully'
    assert category_multiply.objects.count() == 1
    assert company_valuation.objects.count() == 2
    assert company_valuation.objects.first().valuation == 37956965985.166664

    
@pytest.mark.django_db
def test_category_multiple_data_updated_succesfully_if_there__exist_record(api_client,financial_data):
    id=Financial_Data.objects.first().company.subcategory.subcategory_id
    url=reverse('add_multiple')
    response=api_client.post(url,{'price_to_earnings':1,'price_to_revenue':1,'price_to_equity':1.5,'subcategory_id':id})
    response=api_client.post(url,{'price_to_earnings':1,'price_to_revenue':1.5,'price_to_equity':1.5,'subcategory_id':id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message']=='Updated successfully'
    assert category_multiply.objects.count() == 1
    assert company_valuation.objects.count() == 2
    assert company_valuation.objects.first().valuation == 53543204152.0


@pytest.mark.django_db
def test_company_profile_revenue_not_give_error_when_company_id_not_exist(api_client):
    base_url = reverse('company_profile_revenue')
    url = f"{base_url}?name=abc&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_company_profile_generate_revenue_correct_data_when_company_id_exist(api_client,financial_data):
    base_url = reverse('company_profile_revenue')
    url = f"{base_url}?name=KASTRATI GROUP&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Kastrati Group'
    assert response.data['category'] == 'Energji'
    assert response.data['subcategory'] == 'Naftë, Gaz Dhe Lëndë Djegëse'
    assert response.data['revenue_each_year'] == {'2017': 43430576611.0, '2018': 61682523301.0}
    assert response.data['owners']==[]

@pytest.mark.django_db
def test_company_profile_valuation_not_give_error_when_company_id_not_exist(api_client,calculation_data):
    base_url = reverse('company_profile_valuation')
    url = f"{base_url}?name=abc&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_company_profile_generate_valuation_correct_data_when_company_id_exist(api_client,calculation_data):
    base_url = reverse('company_profile_valuation')
    url = f"{base_url}?name=KASTRATI GROUP&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Kastrati Group'
    assert response.data['category'] == 'Energji'
    assert response.data['subcategory'] == 'Naftë, Gaz Dhe Lëndë Djegëse'
    assert response.data['owners']==[]

@pytest.mark.django_db
def test_group_data_file_generate_succesfully_even_if_data_not_present(api_client):
    base_url=reverse('group_data_generate')
    response = api_client.get(base_url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=group_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Group Data')
    assert df.shape[1] ==8
    assert len(df)==0


@pytest.mark.django_db
def test_group_data_file_generate_succesfully_with_data(api_client,subcategory_company_data):
    base_url=reverse('group_data_generate')
    response = api_client.get(base_url)
    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'Content-Disposition' in response
    assert response['Content-Disposition'].startswith('attachment; filename=group_data.xlsx')
    excel_file = BytesIO(response.content)
    df = pd.read_excel(excel_file, sheet_name='Group Data')
    assert df.shape[1] ==8
    assert len(df)==3

@pytest.mark.django_db
def test_group_data_update_succesfully(api_client,group_file):
    url = reverse('group_data_update')
    response = api_client.post(url, {'file':group_file}, format='multipart')
    assert response.status_code == 200
    assert response.data['message'] == 'Group data updated successfully'
    assert Group.objects.all().count() ==3

@pytest.mark.django_db
def test_successful_group_data_ranking(api_client,person_list_data,person_share_data,person_share_2017,calculation_data):
    url = reverse('group_data_ranking',kwargs={'year':2018})
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data['ranking_by_profits']) == 2
    assert len(response.data['ranking_by_valuation']) ==1
    assert len(response.data['ranking_by_revenue']) == 2


@pytest.mark.django_db
def test_successful_group_data_ranking_generate_correctly_even_previous_year_data_not_available(api_client,person_list_data,person_share_2017,calculation_data):
    url = reverse('group_data_ranking',kwargs={'year':2017})
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data['ranking_by_profits']) == 2
    assert len(response.data['ranking_by_valuation']) ==1
    assert len(response.data['ranking_by_revenue']) == 2

@pytest.mark.django_db
def test_successful_group_data_ranking_even_data_not_available(api_client,person_share_2017,calculation_data):
    url = reverse('group_data_ranking',kwargs={'year':2016})
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data['ranking_by_profits']) == 0
    assert len(response.data['ranking_by_valuation']) ==0
    assert len(response.data['ranking_by_revenue']) == 0

@pytest.mark.django_db
def test_group_profile_profit_not_give_error_when_group_id_not_exist(api_client):
    base_url = reverse('group_profile_profit')
    url = f"{base_url}?name=abc&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db  
def test_group_profile_profit_generate_correct_data_when_group_id_exist(api_client,person_list_data,person_share_2017,person_share_data,calculation_data):
    base_url = reverse('group_profile_profit')
    url = f"{base_url}?name=OPERATORI I SHPËRNDARJES SË ENERGJISË ELEKTRIKE GROUP&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'OPERATORI I SHPËRNDARJES SË ENERGJISË ELEKTRIKE GROUP'
    assert response.data['profit'] == 8054551966.0
    assert response.data['profit_each_year'] == {'2017': 6814597753.0,'2018': 8054551966.0}
    assert response.data['companydetails']==[{'image_url': '', 'name': 'GSA', 'profit': 985519000.0, 'share': 100.0, 'subcategory': 'NAFTË, GAZ DHE LËNDË DJEGËSE'}, {'image_url': '', 'name': 'BANKA KOMBETARE TREGTARE', 'profit': 8719656015.0, 'share': 80.0, 'subcategory': 'PAJISJET DHE SHËRBIMET E ENERGJISË'}, {'image_url': '', 'name': 'INTERSIG VIENNA INSURANCE GROUP', 'profit': 93308154.0, 'share': 100.0, 'subcategory': 'PAJISJET DHE SHËRBIMET E ENERGJISË'}]

@pytest.mark.django_db
def test_group_profile_revenue_not_give_error_when_group_id_not_exist(api_client):
    base_url = reverse('group_profile_revenue')
    url = f"{base_url}?name=abc&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_group_profile_revenue_generate_correct_data_when_group_id_exist(api_client,person_list_data,person_share_2017,person_share_data,calculation_data):
    base_url = reverse('group_profile_revenue')
    url = f"{base_url}?name=OPERATORI I SHPËRNDARJES SË ENERGJISË ELEKTRIKE GROUP&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'OPERATORI I SHPËRNDARJES SË ENERGJISË ELEKTRIKE GROUP'
    assert response.data['revenue'] == 28449953692.6
    assert response.data['revenue_each_year'] == {'2017':16999079281.0, '2018': 28449953692.6}
    assert response.data['companydetails']==[{"image_url": "","name": "GSA","revenue": 11209208000.0,"share": 100.0,"subcategory": "NAFTË, GAZ DHE LËNDË DJEGËSE"},{"image_url": "","name": "BANKA KOMBETARE TREGTARE","revenue": 19452311232.0,"share": 80.0,"subcategory": "PAJISJET DHE SHËRBIMET E ENERGJISË"},{"image_url": "","name": "INTERSIG VIENNA INSURANCE GROUP","revenue": 1678896707.0,"share": 100.0,"subcategory": "PAJISJET DHE SHËRBIMET E ENERGJISË"}]

@pytest.mark.django_db
def test_group_profile_valuation_not_give_error_when_group_id_not_exist(api_client):
    base_url = reverse('group_profile_valuation')
    url = f"{base_url}?name=abc&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_group_profile_valuation_generate_correct_data_when_group_id_exist(api_client,person_list_data,person_share_2017,person_share_data,calculation_data):
    base_url = reverse('group_profile_valuation')
    url = f"{base_url}?name=KASTRATI GROUP&year=2018"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'KASTRATI GROUP'
    assert response.data['valuation'] == 448363617021.0
    assert response.data['valuation_each_year'] == {'01-01-2017': 326992071297.0,'01-01-2018': 448363617021.0}
    assert response.data['companydetails']==[{'image_url': '', 'name': 'KASTRATI GROUP', 'valuation': 498181796690.0, 'share': 90.0, 'subcategory': 'NAFTË, GAZ DHE LËNDË DJEGËSE'}]
import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    DROP TABLE IF EXISTS budgets;
    DROP TABLE IF EXISTS receipts;
    DROP TABLE IF EXISTS purchases;
    DROP TABLE IF EXISTS transactions;
    DROP TABLE IF EXISTS users;

    CREATE TABLE 
        public.users (
            id bigint generated by default as identity,
            name text not null,
            email text not null,
            constraint Users_pkey primary key (id),
            constraint users_email_check check (
                (
                    email ~* '^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'::text
                )
            )
        ) tablespace pg_default;

    CREATE TABLE 
        public.transactions (
            id bigint generated by default as identity,
            user_id bigint not null,
            merchant text not null,
            description text null,
            created_at timestamp with time zone not null default now(),
            date text null,
            constraint Transaction_pkey primary key (id),
            constraint transactions_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade
        ) tablespace pg_default;

    CREATE TABLE 
        public.purchases (
            id bigint generated by default as identity,
            transaction_id bigint not null,
            item text not null,
            price integer not null,
            warranty_date text null,
            return_date text null,
            category text not null default 'Other'::text,
            quantity integer not null default 1,
            constraint Purchase_pkey primary key (id),
            constraint purchases_transaction_id_fkey foreign key (transaction_id) references transactions (id) on update cascade on delete cascade,
            constraint purchases_category_check check (
                (
                    category = any (
                        array[
                            'Groceries'::text,
                            'Clothing and Accessories'::text,
                            'Electronics'::text,
                            'Home and Garden'::text,
                            'Health and Beauty'::text,
                            'Entertainment'::text,
                            'Travel'::text,
                            'Automotive'::text,
                            'Services'::text,
                            'Gifts and Special Occasions'::text,
                            'Education'::text,
                            'Fitness and Sports'::text,
                            'Pets'::text,
                            'Office Supplies'::text,
                            'Financial Services'::text,
                            'Other'::text
                        ]
                    )
                )
            ),
            constraint purchases_price_check check ((price >= 0)),
            constraint purchases_quantity_check check ((quantity >= 1))
        ) tablespace pg_default;

    CREATE TABLE 
        public.receipts (
            id bigint generated by default as identity,
            transaction_id bigint null,
            url text not null,
            parsed_data text not null,
            constraint Reciept_pkey primary key (id),
            constraint receipts_transaction_id_fkey foreign key (transaction_id) references transactions (id) on update cascade on delete cascade
        ) tablespace pg_default;

    CREATE TABLE 
        public.budgets (
            id bigint generated by default as identity,
            user_id bigint not null,
            groceries integer not null default 0,
            clothing_and_accessories integer not null default 0,
            electronics integer not null default 0,
            home_and_garden integer not null default 0,
            health_and_beauty integer not null default 0,
            entertainment integer not null default 0,
            travel integer not null default 0,
            automotive integer not null default 0,
            services integer not null default 0,
            gifts_and_special_occasions integer not null default 0,
            education integer not null default 0,
            fitness_and_sports integer not null default 0,
            pets integer not null default 0,
            office_supplies integer not null default 0,
            financial_services integer not null default 0,
            other integer not null default 0,
            constraint budgets_pkey primary key (id),
            constraint budgets_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade,
            constraint budgets_education_check check ((education >= 0)),
            constraint budgets_electronics_check check ((electronics >= 0)),
            constraint budgets_entertainment_check check ((entertainment >= 0)),
            constraint budgets_financial_services_check check ((financial_services >= 0)),
            constraint budgets_fitness_and_sports_check check ((fitness_and_sports >= 0)),
            constraint budgets_gifts_and_special_occasions_check check ((gifts_and_special_occasions >= 0)),
            constraint budgets_groceries_check check ((groceries >= 0)),
            constraint budgets_automotive_check check ((automotive >= 0)),
            constraint budgets_home_and_garden_check check ((home_and_garden >= 0)),
            constraint budgets_office_supplies_check check ((office_supplies >= 0)),
            constraint budgets_other_check check ((other >= 0)),
            constraint budgets_pets_check check ((pets >= 0)),
            constraint budgets_services_check check ((services >= 0)),
            constraint budgets_travel_check check ((travel >= 0)),
            constraint budgets_health_and_beauty_check check ((health_and_beauty >= 0)),
            constraint budgets_clothing_and_accessories_check check ((clothing_and_accessories >= 0))
        ) tablespace pg_default;
    """))

# 60,000 for 1 mil rows fake data
num_users = 1000
fake = Faker()

# create fake users
with engine.begin() as conn:
    print("creating fake users...")
    for i in range(num_users):
        if (i % 10 == 0):
            print(i)

        user_id = conn.execute(sqlalchemy.text("""
        INSERT INTO public.users (name, email) VALUES (:name, :email) RETURNING id;
        """), {"name": fake.name(), "email": fake.email()}).scalar_one()

        # create fake transactions
        num_transactions = np.random.randint(1, 5)
        for j in range(num_transactions):
            merchant = fake.company()
            description = fake.sentence()
            date = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=None)
            
            transaction_id = conn.execute(sqlalchemy.text("""
            INSERT INTO public.transactions (user_id, merchant, description, created_at, date) 
            VALUES (:user_id, :merchant, :description, :created_at, :date) RETURNING id;
            """), {"user_id": user_id, "merchant": merchant, "description": description, "created_at": date, "date": date}).scalar_one()

            # create fake purchases
            num_purchases = np.random.randint(1, 5)
            for k in range(num_purchases):
                item = fake.word()
                price = np.random.randint(1, 100)
                warranty_date = fake.date_between(start_date='now', end_date='+1y').strftime("%Y-%m-%d")
                return_date = fake.date_between(start_date='+1d', end_date='+1y').strftime("%Y-%m-%d")
                category = fake.random_element(elements=['Groceries', 'Clothing and Accessories', 'Electronics', 'Home and Garden', 
                                                        'Health and Beauty', 'Entertainment', 'Travel', 'Automotive', 
                                                        'Services', 'Gifts and Special Occasions', 'Education', 
                                                        'Fitness and Sports', 'Pets', 'Office Supplies', 
                                                        'Financial Services', 'Other'])
                quantity = np.random.randint(1, 10)

                purchase_id = conn.execute(sqlalchemy.text("""
                INSERT INTO public.purchases (transaction_id, item, price, warranty_date, return_date, category, quantity) 
                VALUES (:transaction_id, :item, :price, :warranty_date, :return_date, :category, :quantity) RETURNING id;
                """), {"transaction_id": transaction_id, "item": item, "price": price, 
                       "warranty_date": warranty_date, "return_date": return_date, 
                       "category": category, "quantity": quantity}).scalar_one()

                # create fake receipts
                url = fake.uri()
                parsed_data = fake.text()
                conn.execute(sqlalchemy.text("""
                INSERT INTO public.receipts (transaction_id, url, parsed_data) 
                VALUES (:transaction_id, :url, :parsed_data);
                """), {"transaction_id": transaction_id, "url": url, "parsed_data": parsed_data})

        # create fake budgets for users
        conn.execute(sqlalchemy.text("""
        INSERT INTO public.budgets (user_id, groceries, clothing_and_accessories, electronics, home_and_garden, 
                                     health_and_beauty, entertainment, travel, automotive, services, 
                                     gifts_and_special_occasions, education, fitness_and_sports, pets, 
                                     office_supplies, financial_services, other) 
        VALUES (:user_id, :groceries, :clothing_and_accessories, :electronics, :home_and_garden, 
                :health_and_beauty, :entertainment, :travel, :automotive, :services, 
                :gifts_and_special_occasions, :education, :fitness_and_sports, :pets, 
                :office_supplies, :financial_services, :other);
        """), {"user_id": user_id,
               "groceries": np.random.randint(50, 500),
               "clothing_and_accessories": np.random.randint(50, 500),
               "electronics": np.random.randint(50, 500),
               "home_and_garden": np.random.randint(50, 500),
               "health_and_beauty": np.random.randint(50, 500),
               "entertainment": np.random.randint(50, 500),
               "travel": np.random.randint(50, 500),
               "automotive": np.random.randint(50, 500),
               "services": np.random.randint(50, 500),
               "gifts_and_special_occasions": np.random.randint(50, 500),
               "education": np.random.randint(50, 500),
               "fitness_and_sports": np.random.randint(50, 500),
               "pets": np.random.randint(50, 500),
               "office_supplies": np.random.randint(50, 500),
               "financial_services": np.random.randint(50, 500),
               "other": np.random.randint(50, 500),
              })

print("Fake data generation completed.")

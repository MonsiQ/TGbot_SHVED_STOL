PGDMP  ;                
    |         
   shved_stol    17.0    17.0 %    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    16406 
   shved_stol    DATABASE     ~   CREATE DATABASE shved_stol WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE shved_stol;
                     postgres    false            �            1259    16424    dishes    TABLE     �   CREATE TABLE public.dishes (
    dish_id integer NOT NULL,
    dish_name character varying(255) NOT NULL,
    dish_description text,
    meal character varying(50) NOT NULL
);
    DROP TABLE public.dishes;
       public         heap r       postgres    false            �            1259    16423    dishes_dish_id_seq    SEQUENCE     �   CREATE SEQUENCE public.dishes_dish_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.dishes_dish_id_seq;
       public               postgres    false    218            �           0    0    dishes_dish_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.dishes_dish_id_seq OWNED BY public.dishes.dish_id;
          public               postgres    false    217            �            1259    16457    order_dishes    TABLE     Y   CREATE TABLE public.order_dishes (
    order_id integer NOT NULL,
    dish_id integer
);
     DROP TABLE public.order_dishes;
       public         heap r       postgres    false            �            1259    16456    order_dishes_order_id_seq    SEQUENCE     �   CREATE SEQUENCE public.order_dishes_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.order_dishes_order_id_seq;
       public               postgres    false    223            �           0    0    order_dishes_order_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.order_dishes_order_id_seq OWNED BY public.order_dishes.order_id;
          public               postgres    false    222            �            1259    16445    orders    TABLE       CREATE TABLE public.orders (
    order_id integer NOT NULL,
    user_id integer,
    delivery_date date NOT NULL,
    "time" character varying(50) NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP(0)
);
    DROP TABLE public.orders;
       public         heap r       postgres    false            �            1259    16444    orders_order_id_seq    SEQUENCE     �   CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.orders_order_id_seq;
       public               postgres    false    221            �           0    0    orders_order_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;
          public               postgres    false    220            �            1259    16472    tables    TABLE     �   CREATE TABLE public.tables (
    table_number integer NOT NULL,
    seats_count integer NOT NULL,
    occupied_seats_count integer NOT NULL
);
    DROP TABLE public.tables;
       public         heap r       postgres    false            �            1259    16471    tables_table_number_seq    SEQUENCE     �   CREATE SEQUENCE public.tables_table_number_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.tables_table_number_seq;
       public               postgres    false    225            �           0    0    tables_table_number_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.tables_table_number_seq OWNED BY public.tables.table_number;
          public               postgres    false    224            �            1259    16439    users    TABLE     �   CREATE TABLE public.users (
    user_id bigint NOT NULL,
    full_name character varying(255),
    departure_date date,
    table_number integer,
    seat_number integer,
    status character varying(50)
);
    DROP TABLE public.users;
       public         heap r       postgres    false            4           2604    16427    dishes dish_id    DEFAULT     p   ALTER TABLE ONLY public.dishes ALTER COLUMN dish_id SET DEFAULT nextval('public.dishes_dish_id_seq'::regclass);
 =   ALTER TABLE public.dishes ALTER COLUMN dish_id DROP DEFAULT;
       public               postgres    false    217    218    218            7           2604    16460    order_dishes order_id    DEFAULT     ~   ALTER TABLE ONLY public.order_dishes ALTER COLUMN order_id SET DEFAULT nextval('public.order_dishes_order_id_seq'::regclass);
 D   ALTER TABLE public.order_dishes ALTER COLUMN order_id DROP DEFAULT;
       public               postgres    false    223    222    223            5           2604    16448    orders order_id    DEFAULT     r   ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);
 >   ALTER TABLE public.orders ALTER COLUMN order_id DROP DEFAULT;
       public               postgres    false    220    221    221            8           2604    16475    tables table_number    DEFAULT     z   ALTER TABLE ONLY public.tables ALTER COLUMN table_number SET DEFAULT nextval('public.tables_table_number_seq'::regclass);
 B   ALTER TABLE public.tables ALTER COLUMN table_number DROP DEFAULT;
       public               postgres    false    224    225    225            �          0    16424    dishes 
   TABLE DATA           L   COPY public.dishes (dish_id, dish_name, dish_description, meal) FROM stdin;
    public               postgres    false    218   *       �          0    16457    order_dishes 
   TABLE DATA           9   COPY public.order_dishes (order_id, dish_id) FROM stdin;
    public               postgres    false    223   �+       �          0    16445    orders 
   TABLE DATA           ^   COPY public.orders (order_id, user_id, delivery_date, "time", status, created_at) FROM stdin;
    public               postgres    false    221   �+       �          0    16472    tables 
   TABLE DATA           Q   COPY public.tables (table_number, seats_count, occupied_seats_count) FROM stdin;
    public               postgres    false    225   ,       �          0    16439    users 
   TABLE DATA           f   COPY public.users (user_id, full_name, departure_date, table_number, seat_number, status) FROM stdin;
    public               postgres    false    219   <,       �           0    0    dishes_dish_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.dishes_dish_id_seq', 6, true);
          public               postgres    false    217            �           0    0    order_dishes_order_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.order_dishes_order_id_seq', 1, false);
          public               postgres    false    222            �           0    0    orders_order_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.orders_order_id_seq', 1, true);
          public               postgres    false    220            �           0    0    tables_table_number_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.tables_table_number_seq', 1, false);
          public               postgres    false    224            :           2606    16431    dishes dishes_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY public.dishes
    ADD CONSTRAINT dishes_pkey PRIMARY KEY (dish_id);
 <   ALTER TABLE ONLY public.dishes DROP CONSTRAINT dishes_pkey;
       public                 postgres    false    218            >           2606    16450    orders orders_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);
 <   ALTER TABLE ONLY public.orders DROP CONSTRAINT orders_pkey;
       public                 postgres    false    221            @           2606    16477    tables tables_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.tables
    ADD CONSTRAINT tables_pkey PRIMARY KEY (table_number);
 <   ALTER TABLE ONLY public.tables DROP CONSTRAINT tables_pkey;
       public                 postgres    false    225            <           2606    16480    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public                 postgres    false    219            B           2606    16466 &   order_dishes order_dishes_dish_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.order_dishes
    ADD CONSTRAINT order_dishes_dish_id_fkey FOREIGN KEY (dish_id) REFERENCES public.dishes(dish_id);
 P   ALTER TABLE ONLY public.order_dishes DROP CONSTRAINT order_dishes_dish_id_fkey;
       public               postgres    false    4666    223    218            C           2606    16461 '   order_dishes order_dishes_order_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.order_dishes
    ADD CONSTRAINT order_dishes_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);
 Q   ALTER TABLE ONLY public.order_dishes DROP CONSTRAINT order_dishes_order_id_fkey;
       public               postgres    false    4670    223    221            A           2606    16481    orders orders_user_id_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 D   ALTER TABLE ONLY public.orders DROP CONSTRAINT orders_user_id_fkey;
       public               postgres    false    219    221    4668            �   _  x��R[R�@�ޜ"HQ��4&E-(����BVBX�
=7�g5�`Y�Hv����''���KKc�
;�G�j���Fn��	�z7D��ܠ&>���V��2�G���X�=������\���:���ᑟ^5�P�,F��J�'R�,c,�T��K����t��V�8�y�K�X�z�k:������35P���ӘJYdWR����\������.��
<KF���;+���Ab�	<����E���eFd�Q��D�ҭ�
��u��팉��|���B3���&_�%z���i�=$9��]S�.�,r'��XY���伖��>��"I3��bRU}$���w����(��X�D      �      x�3�4����� ]      �   O   x�3�4�44��4�4��4202�54�54ἰ��.6]l һ8A�Ŧ;.l���b����F
�&VFV�\1z\\\ 	�      �      x�3�4�4�2�&`�LIC�=... K�)      �   \   x�3�44��4�4��0����/��M
�\�pa�v+\�qa�}@�v\l�4202�50"N*�u�	�tӅ��/������ $�-a     
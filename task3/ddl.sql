--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: director; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.director (
    "ID" bigint NOT NULL,
    "FULL_NAME" character varying,
    "IMDB_LINK" character varying
);


ALTER TABLE public.director OWNER TO postgres;

--
-- Name: movie; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movie (
    "ID" bigint NOT NULL,
    "TITLE" character varying,
    "DESCRIPTION" text,
    "ORIGINAL_TITLE" character varying,
    "NOW_PLAYING" boolean,
    "LAST_UPDATE_DATE" date
);


ALTER TABLE public.movie OWNER TO postgres;

--
-- Name: movie_director; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movie_director (
    "MOVIE_ID" bigint NOT NULL,
    "DIRECTOR_ID" bigint NOT NULL
);


ALTER TABLE public.movie_director OWNER TO postgres;

--
-- Name: movie_director MOVIE_DIRECTOR_ID; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_director
    ADD CONSTRAINT "MOVIE_DIRECTOR_ID" PRIMARY KEY ("MOVIE_ID", "DIRECTOR_ID");


--
-- Name: director director_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.director
    ADD CONSTRAINT director_pkey PRIMARY KEY ("ID");


--
-- Name: movie movie_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie
    ADD CONSTRAINT movie_pkey PRIMARY KEY ("ID");


--
-- Name: director_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX director_id_index ON public.director USING btree ("ID") INCLUDE ("ID") WITH (deduplicate_items='true');


--
-- Name: movie_director DIRECTOR_ID; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_director
    ADD CONSTRAINT "DIRECTOR_ID" FOREIGN KEY ("DIRECTOR_ID") REFERENCES public.director("ID") NOT VALID;


--
-- Name: movie_director MOVIE_ID; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movie_director
    ADD CONSTRAINT "MOVIE_ID" FOREIGN KEY ("MOVIE_ID") REFERENCES public.movie("ID");


--
-- PostgreSQL database dump complete
--


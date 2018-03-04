CREATE TABLE "League" (
	"id_league" serial NOT NULL,
	"name_league" varchar(100) NOT NULL,
	"url_league" varchar(300) NOT NULL UNIQUE,
	"id_country" int NOT NULL,
	"id_sport" int NOT NULL,
	"status_league" bool NOT NULL DEFAULT 'FALSE',
	CONSTRAINT League_pk PRIMARY KEY ("id_league")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Country" (
	"id_country" serial NOT NULL,
	"name_country" varchar(100) NOT NULL,
	CONSTRAINT Country_pk PRIMARY KEY ("id_country")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Match" (
	"id_match" serial NOT NULL,
	"url_match" varchar(300) NOT NULL UNIQUE,
	"id_league" int NOT NULL,
	"id_home_team" int NOT NULL,
	"id_guest_team" int NOT NULL,
	"time_match" TIMESTAMP NOT NULL,
	"id_match_token" int NOT NULL,
	"id_match_ratio" int,
	"id_match_status" int,
	CONSTRAINT Match_pk PRIMARY KEY ("id_match")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Team" (
	"id_team" serial NOT NULL,
	"name_team" varchar(100) NOT NULL,
	"url_team" varchar(300) NOT NULL UNIQUE,
	CONSTRAINT Team_pk PRIMARY KEY ("id_team")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Sport" (
	"id_sport" serial NOT NULL,
	"name_sport" varchar(30) NOT NULL UNIQUE,
	CONSTRAINT Sport_pk PRIMARY KEY ("id_sport")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "MatchScore" (
	"id_match_score" serial NOT NULL,
	"id_score" int NOT NULL,
	"id_match" int NOT NULL,
	CONSTRAINT MatchScore_pk PRIMARY KEY ("id_match_score")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Score" (
	"id_score" serial NOT NULL,
	"home_score" int NOT NULL,
	"guest_score" int NOT NULL,
	"time_score" TIMESTAMP NOT NULL,
	CONSTRAINT Score_pk PRIMARY KEY ("id_score")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Status" (
	"id_match_status" serial NOT NULL,
	"started_status" bool NOT NULL,
	"finished_status" bool NOT NULL,
	"canceled_status" bool NOT NULL,
	CONSTRAINT Status_pk PRIMARY KEY ("id_match_status")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "MatchToken" (
	"id_match_token" serial NOT NULL,
	"hash_token" int NOT NULL,
	"match_token" int NOT NULL,
	"sport_token" int NOT NULL,
	"version_token" int NOT NULL,
	CONSTRAINT MatchToken_pk PRIMARY KEY ("id_match_token")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Bookmaker" (
	"id_bookmaker" serial NOT NULL,
	"name_bookmaker" varchar(30) NOT NULL,
	CONSTRAINT Bookmaker_pk PRIMARY KEY ("id_bookmaker")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "TokenBookmaker" (
	"id_token_bookmaker" serial NOT NULL,
	"id_bookmaker" int NOT NULL,
	"id_ratio_token" int NOT NULL,
	CONSTRAINT TokenBookmaker_pk PRIMARY KEY ("id_token_bookmaker")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "RatioToken" (
	"id_ratio_token" serial NOT NULL,
	"ratio_token" varchar(20) NOT NULL,
	"index_token" int NOT NULL,
	"id_calc_ratio" int(20) NOT NULL,
	"id_match" int NOT NULL,
	CONSTRAINT RatioToken_pk PRIMARY KEY ("id_ratio_token")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Ratio" (
	"id_ratio" serial NOT NULL,
	"time_ratio" TIMESTAMP NOT NULL,
	"ratio" float4 NOT NULL,
	CONSTRAINT Ratio_pk PRIMARY KEY ("id_ratio")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "CalcRatio" (
	"id_calc_ratio" serial NOT NULL,
	"name_calc_ratio" varchar(10) NOT NULL UNIQUE,
	CONSTRAINT CalcRatio_pk PRIMARY KEY ("id_calc_ratio")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "UserAccount" (
	"id_user" serial NOT NULL,
	"login_user" varchar(50) NOT NULL UNIQUE,
	"password_user" varchar(50) NOT NULL,
	CONSTRAINT UserAccount_pk PRIMARY KEY ("id_user")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "UserMatch" (
	"id_user_match" serial NOT NULL,
	"id_match" int NOT NULL,
	"id_user" int NOT NULL,
	"id_time_zone" int NOT NULL,
	"comment_user_match" TEXT,
	CONSTRAINT UserMatch_pk PRIMARY KEY ("id_user_match")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "TokenBookmakerRatio" (
	"id_token_bookmaker_ratio" serial NOT NULL,
	"id_ratio" bigint NOT NULL,
	"id_token_bookmaker" bigint NOT NULL,
	CONSTRAINT TokenBookmakerRatio_pk PRIMARY KEY ("id_token_bookmaker_ratio")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "TeamLeague" (
	"id_team_league" serial NOT NULL,
	"id_team" int NOT NULL,
	"id_league" int NOT NULL,
	CONSTRAINT TeamLeague_pk PRIMARY KEY ("id_team_league")
) WITH (
  OIDS=FALSE
);

CREATE TABLE "Timezone" (
	"id_time_zone" serial NOT NULL,
	"name_time_zone" varchar(10) NOT NULL UNIQUE,
	CONSTRAINT Timezone_pk PRIMARY KEY ("id_time_zone")
) WITH (
  OIDS=FALSE
);

ALTER TABLE "League" ADD CONSTRAINT "League_fk0" FOREIGN KEY ("id_country") REFERENCES "Country"("id_country");
ALTER TABLE "League" ADD CONSTRAINT "League_fk1" FOREIGN KEY ("id_sport") REFERENCES "Sport"("id_sport");

ALTER TABLE "Match" ADD CONSTRAINT "Match_fk0" FOREIGN KEY ("id_league") REFERENCES "League"("id_league");
ALTER TABLE "Match" ADD CONSTRAINT "Match_fk1" FOREIGN KEY ("id_home_team") REFERENCES "Team"("id_team");
ALTER TABLE "Match" ADD CONSTRAINT "Match_fk2" FOREIGN KEY ("id_guest_team") REFERENCES "Team"("id_team");
ALTER TABLE "Match" ADD CONSTRAINT "Match_fk3" FOREIGN KEY ("id_match_token") REFERENCES "MatchToken"("id_match_token");
ALTER TABLE "Match" ADD CONSTRAINT "Match_fk4" FOREIGN KEY ("id_match_ratio") REFERENCES "MatchRatio"("id_match_ratio");
ALTER TABLE "Match" ADD CONSTRAINT "Match_fk5" FOREIGN KEY ("id_match_status") REFERENCES "Status"("id_match_status");

ALTER TABLE "MatchScore" ADD CONSTRAINT "MatchScore_fk0" FOREIGN KEY ("id_score") REFERENCES "Score"("id_score");
ALTER TABLE "MatchScore" ADD CONSTRAINT "MatchScore_fk1" FOREIGN KEY ("id_match") REFERENCES "Match"("id_match");

ALTER TABLE "TokenBookmaker" ADD CONSTRAINT "TokenBookmaker_fk0" FOREIGN KEY ("id_bookmaker") REFERENCES "Bookmaker"("id_bookmaker");
ALTER TABLE "TokenBookmaker" ADD CONSTRAINT "TokenBookmaker_fk1" FOREIGN KEY ("id_ratio_token") REFERENCES "RatioToken"("id_ratio_token");

ALTER TABLE "RatioToken" ADD CONSTRAINT "RatioToken_fk0" FOREIGN KEY ("id_calc_ratio") REFERENCES "CalcRatio"("id_calc_ratio");
ALTER TABLE "RatioToken" ADD CONSTRAINT "RatioToken_fk1" FOREIGN KEY ("id_match") REFERENCES "Match"("id_match");

ALTER TABLE "UserMatch" ADD CONSTRAINT "UserMatch_fk0" FOREIGN KEY ("id_match") REFERENCES "Match"("id_match");
ALTER TABLE "UserMatch" ADD CONSTRAINT "UserMatch_fk1" FOREIGN KEY ("id_user") REFERENCES "UserAccount"("id_user");
ALTER TABLE "UserMatch" ADD CONSTRAINT "UserMatch_fk2" FOREIGN KEY ("id_time_zone") REFERENCES "Timezone"("id_time_zone");

ALTER TABLE "TokenBookmakerRatio" ADD CONSTRAINT "TokenBookmakerRatio_fk0" FOREIGN KEY ("id_ratio") REFERENCES "Ratio"("id_ratio");
ALTER TABLE "TokenBookmakerRatio" ADD CONSTRAINT "TokenBookmakerRatio_fk1" FOREIGN KEY ("id_token_bookmaker") REFERENCES "TokenBookmaker"("id_token_bookmaker");

ALTER TABLE "TeamLeague" ADD CONSTRAINT "TeamLeague_fk0" FOREIGN KEY ("id_team") REFERENCES "Team"("id_team");
ALTER TABLE "TeamLeague" ADD CONSTRAINT "TeamLeague_fk1" FOREIGN KEY ("id_league") REFERENCES "League"("id_league");

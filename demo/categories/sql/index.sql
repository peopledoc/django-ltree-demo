-- used when we access the path directly
CREATE INDEX categories_category_path
          ON categories_category
       USING btree(path);

-- used when we get descendants or ancestors
CREATE INDEX categories_category_path_gist
          ON categories_category
       USING GIST(path);

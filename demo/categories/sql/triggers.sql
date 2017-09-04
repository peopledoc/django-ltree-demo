-- function to calculate the path of any given category
CREATE OR REPLACE FUNCTION _update_category_path() RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.parent_id IS NULL THEN
        NEW.path = NEW.code::ltree;
    ELSE
        SELECT path || NEW.code
          FROM categories_category
         WHERE NEW.parent_id IS NULL or id = NEW.parent_id
          INTO NEW.path;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- function to update the path of the descendants of a category
CREATE OR REPLACE FUNCTION _update_descendants_category_path() RETURNS TRIGGER AS
$$
BEGIN
    UPDATE categories_category
       SET path = NEW.path || subpath(categories_category.path, nlevel(OLD.path))
     WHERE categories_category.path <@ OLD.path AND id != NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- calculate the path every time we insert a new category
DROP TRIGGER IF EXISTS category_path_insert_trg ON categories_category;
CREATE TRIGGER category_path_insert_trg
               BEFORE INSERT ON categories_category
               FOR EACH ROW
               EXECUTE PROCEDURE _update_category_path();


-- calculate the path when updating the parent or the code
DROP TRIGGER IF EXISTS category_path_update_trg ON categories_category;
CREATE TRIGGER category_path_update_trg
               BEFORE UPDATE ON categories_category
               FOR EACH ROW
               WHEN (OLD.parent_id IS DISTINCT FROM NEW.parent_id
                     OR OLD.code IS DISTINCT FROM NEW.code)
               EXECUTE PROCEDURE _update_category_path();


-- if the path was updated, update the path of the descendants
DROP TRIGGER IF EXISTS category_path_after_trg ON categories_category;
CREATE TRIGGER category_path_after_trg
               AFTER UPDATE ON categories_category
               FOR EACH ROW
               WHEN (NEW.path IS DISTINCT FROM OLD.path)
               EXECUTE PROCEDURE _update_descendants_category_path();
